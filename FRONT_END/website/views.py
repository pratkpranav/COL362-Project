from os import defpath, stat
import webbrowser
from flask import Blueprint, render_template, flash, request, redirect, jsonify
from flask.helpers import url_for
from flask_login import  current_user, logout_user, login_user, login_required
from website.database import *
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import website
import logging
import json
import os
import random
import ast
import time

views = Blueprint('views', __name__)

@website.login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('auth.login'))

def handle_submission(id, index,  author, lang):

    rr = random.randint(0, 10)
    ongoing_contests = db_get_ongoing_contests(website.db, website.dbConn)

    verdict = "WRONG_ANSWER"
    sid = random.randint(144210990, 1000000000000)
    tCons = 23
    mbyte = 2321

    if rr == 0:
        verdict = "OK"

    typ = "PRACTICE"
    ok = 1
    for contest in ongoing_contests:
        if id == website.Contest(contest).contestId:
            ok = 0
            break
    if ok == 0:
        typ = "CONTESTANT"

    stime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sub = website.Submission((sid, id, typ, index, author, lang, verdict, tCons, mbyte, stime) )
    current = time.time()
    db_add_submission(website.db, website.dbConn, sub)
    next = time.time()
    logging.info('Timing Plot Add submission: %lf', next-current)
     
    return


@views.route('/', methods=['GET', 'POST'])
def home():
    current = time.time()
    db_blog_delete_triggers(website.db, website.dbConn)
    next = time.time()
    logging.info('Timing Plot delete triggers: %lf', next-current)
    
    logging.info("Home page is requested") 
    num_top_rated = int(website.parser['home_page']['num_top_rated'])
    num_top_contributors = int(website.parser['home_page']['num_top_contributors'])
    current = time.time()
    top_rated_users = db_get_top_rated_users(website.db, website.dbConn, num_top_rated)
    next = time.time()
    logging.info('Timing Plot Add top rated users: %lf', next-current)
    
    current = time.time()
    top_contributors_users = db_get_top_contributors_users(website.db, website.dbConn, num_top_contributors)
    next = time.time()
    logging.info('Timing Plot Add top contributors: %lf', next-current)
    
    current = time.time()
    top_blogs = db_top_blogs(website.db, website.dbConn)
    next = time.time()
    logging.info('Timing Plot Add top blogs: %lf', next-current)
    
    return render_template("home.html", user=current_user, top_rated_users = top_rated_users, top_contributors_users= top_contributors_users, top_blogs = top_blogs) 

# @views.route('/profile/<handle>/home', methods=['GET', 'POST'])
# def profilehome(handle):
    # logging.debug("User: %s profile was requested", handle)
    # return render_template("profile_home.html", user=current_user)

@views.route('/profile/<handle>/blog', methods=['GET', 'POST'])
def profileblog(handle):
    logging.debug("User: %s blogs was requested", handle)
    return render_template("profile_blog.html", user=current_user)

@views.route('/profile/<handle>/contest', methods=['GET', 'POST'])
def profilecontest(handle):
    logging.debug("User: %s contests was requested", handle)
    return render_template("profile_contest.html", user=current_user)

@views.route('/profile/<handle>/submission', methods=['GET', 'POST'])
def profilesubmission(handle):
    logging.debug("User: %s submission was requested", handle)
    return render_template("profile_submission.html", user=current_user)

@views.route('/profile/<handle>/friend', methods=['GET', 'POST'])
def profilefriend(handle):
    logging.debug("User: %s friends was requested", handle)
    return render_template("profile_friend.html", user=current_user)

@views.route('/profile/<handle>', methods=['GET', 'POST'])
def profile(handle):
    #TODO, pass both current_user and handle into the render_template
    logging.info("User: %s profile was requested", handle)
    
    profile_user = db_get_user_with_handle(website.db, website.dbConn, handle)
    if profile_user == None:
        return redirect(url_for('views.home'))
    
    profile_userObj = website.User(profile_user)
    current = time.time()
    profile_user_friends = db_get_num_followers(website.db, website.dbConn, handle)
    next = time.time()
    logging.info('Timing Plot num followers: %lf', next-current)
    
    profile_userObj.numfollowers = profile_user_friends

    user_follows_profile = False
    if current_user.is_authenticated:
        current = time.time()
        user_follows_profile = db_is_follower(website.db, website.dbConn, current_user.handle, profile_userObj.handle) 
        next = time.time()
        logging.info('Timing Plot is following: %lf', next-current)
    

    return render_template("profile_home.html", user=current_user, profile_user = profile_userObj, user_follows_profile = user_follows_profile)


#TODO: make this user sepecific
user_attribute_store = dict()
#ideally we should not maintain this
#but kya kare itna atta nahi hai hume


@views.route('/users', methods=['GET', 'POST'])
def users():
    logging.info("Users search page request")
    #if request.method == 'POST':
    #no need to handle it separately

    if request.method == 'POST' or len(user_attribute_store) == 0:
        user_attribute_store['country'] = request.form.get('country', default = "", type=str)
        user_attribute_store['handle'] = request.form.get('handle', default = "", type=str) 
        user_attribute_store['rcmp'] = request.form.get('ratcmp', default="ge", type=str)
        user_attribute_store['rating'] = request.form.get('rating', default=0, type=int)
        user_attribute_store['ctrbcmp'] = request.form.get('ctrbcmp', default="ge", type=str)
        user_attribute_store['contributions'] = request.form.get('contribution', default=0, type=int)
        user_attribute_store['fcmp'] = request.form.get('fcmp', default="ge", type=str)
        user_attribute_store['numfollowers'] = request.form.get('numfollowers', default=0, type=int)
        user_attribute_store['cnstcmp'] = request.form.get('cnstcmp', default="ge", type=str)
        user_attribute_store['numcontests'] = request.form.get('numcontests', default=0, type=int)

    curr_page = request.args.get('pageNo', default=1, type=int)
    users_per_page = int(website.parser['users']['users_per_page'])
    current = time.time()
    users = db_get_users_with(website.db, website.dbConn, 
            user_attribute_store['country'],
            user_attribute_store['handle'],
            user_attribute_store['rcmp'],
            user_attribute_store['rating'],
            user_attribute_store['ctrbcmp'],
            user_attribute_store['contributions'],
            user_attribute_store['fcmp'],
            user_attribute_store['numfollowers'],
            user_attribute_store['cnstcmp'],
            user_attribute_store['numcontests'],
            (curr_page-1)*users_per_page, users_per_page+1)
    next = time.time()
    logging.info('Timing Plot User query: %lf', next-current)
    
    if curr_page != 1 and len(users) == 0:
        return redirect(url_for('views.users') + '?pageNo=1'  )

    first_page = (curr_page == 1)
    last_page = False

    if len(users) != users_per_page + 1:
        last_page = True
    else:
        users.pop()

    current = time.time()
    countries = db_get_countries(website.db, website.dbConn)
    next = time.time()
    logging.info('Timing Plot Add top rated users: %lf', next-current)
    
    return render_template("users.html", user = current_user, users= users, countries = countries, first_page = first_page, last_page =last_page, curr_page = curr_page)


#TODO make this separate for each user
problem_set_tag_store = dict()

@views.route('/problemSet', methods=['GET', 'POST'])
def problemSet():
    handle_upcoming_contests()
    if request.method == 'POST' or len(problem_set_tag_store) == 0:
        problem_set_tag_store['rating'] = request.form.get('rating', default=0, type=int)
        problem_set_tag_store['rcmp'] = request.form.get('rcmp', default="ge", type=int)
        problem_set_tag_store['tags'] = request.form.getlist('tags')

    curr_page = request.args.get('pageNo', default = 1, type=int)
    problems_per_page = int(website.parser['users']['problems_per_page'])

    logging.debug("Rating: %s", problem_set_tag_store['rating'])
    logging.debug("Tags: [")
    for tag in problem_set_tag_store['tags']:
        logging.debug("%s,", tag)
    logging.debug("]")

    current = time.time()
    problems = db_get_problems_with(website.db, website.dbConn, 
            problem_set_tag_store['rating'], 
            problem_set_tag_store['rcmp'],
            problem_set_tag_store['tags'],
            (curr_page-1)*problems_per_page, problems_per_page+1)
    next = time.time()
    logging.info('Timing Plot get problems: %lf', next-current)
    
            

    if curr_page != 1 and len(problems) == 0:
        return redirect(url_for('views.problemSet') + '?pageNo=1'  )

    first_page = (curr_page == 1)
    last_page = False
    if len(problems) != problems_per_page + 1:
        last_page = True
    else:
        problems.pop()

    for (idx, problem) in enumerate(problems):
        problems[idx] = website.Problem(problem)

    current = time.time()
    all_tags = db_get_all_problem_tags(website.db, website.dbConn)
    next = time.time()
    logging.info('Timing Plot All problem tags: %lf', next-current)
    

    # all_tags = db_get_all_problem_tags(website.db, website.dbConn)
    return render_template("problemSet.html", user = current_user, all_tags = all_tags, problems = problems, curr_page=curr_page, first_page=first_page, last_page=last_page)



@views.route('/profile/<handle>/edit', methods=['GET', 'POST'])
def account(handle):

    logging.info("User: %s, Request Type: %s, Page: edit profile", handle, request.method)

    current = time.time()
    user = db_get_user_with_handle(website.db, website.dbConn, handle)
    next = time.time()
    logging.info('Timing Plot get user with handle: %lf', next-current)
    
    if not current_user.is_authenticated:
        logging.debug("Edit profile page for user: %s, was requrest without login", handle)
        return redirect(url_for('views.profile', handle=handle))
    elif user:
        userObj = website.User(user)
        logging.debug("User %s exists in database. Check authorization", userObj.handle)
            
        if current_user.handle != userObj.handle:
            logging.debug("User %s is not authorizaed to edit user %s, redirecting to view profile page", current_user.handle, userObj.handle)
            return redirect(url_for('views.profile', handle=handle))

    else:
        logging.debug("No such user exists, redirecting to home page")
        return redirect(url_for('views.home'))


    if request.method == 'POST':
        logging.info("Received post request on edit profile page")
        new_firstname = request.form.get('firstname')
        new_lastname = request.form.get('lastname')
        new_handle = request.form.get('handle')
        new_country = request.form.get('country')
        new_password1 = request.form.get('password1')
        new_password2 = request.form.get('password2')
        
        if new_handle != "":
            userObj.handle = new_handle
        current = time.time()
        handle_already_exists = (None != db_get_user_with_handle(website.db, website.dbConn, new_handle))
        next = time.time()
        logging.info('Timing Plot get user with handle: %lf', next-current)
    
        if handle_already_exists:
            logging.debug("User requested for an already in use handle")
            flash('Handle already taken by some other user', category='error')
            return render_template("profile_edit.html", user=current_user)

        if new_firstname != "":
            userObj.firstname = new_firstname
        if new_lastname != "":
            userObj.lastname = new_lastname
        if new_country != "":
            userObj.country = new_country
        if new_password1 != new_password2:
            logging.debug("User entered non-matching passwords")
            flash("Password don't match", category='error')
            return render_template("profile_edit.html", user=current_user)

        if new_password1 != "":
            logging.debug("User entered a new password")
            userObj.password = generate_password_hash(new_password1, method='sha256')

        current = time.time()
        db_update_user(website.db, website.dbConn, current_user.handle, userObj)
        next = time.time()
        logging.info('Timing Plot update user: %lf', next-current)
    
        flash('Profile Updated!', category='success')
        
        logout_user()

        login_user(userObj, remember=True)

        return redirect(url_for('views.profile', handle=handle))

    #handle get request here
    logging.info("Authorization Successful, User %s is on edit profile page", userObj.handle)
    return render_template("profile_edit.html", user=current_user)

@views.route('/deleteProfile/<handle>', methods=['GET', 'POST'])
def delete_account(handle):
    #only post methods are accepted
    #delete the account of the user currently logged in
    #and then logout and redirect to home page
    
    logging.info("Got Account delete requres from user: %s", handle)
    assert db_get_user_with_handle(website.db, website.dbConn, current_user.handle) != None


    logging.info("Deleting user from database")
    current = time.time()
    event = db_delete_user(website.db, website.dbConn, current_user.handle)
    next = time.time()
    logging.info('Timing Plot delete user: %lf', next-current)
    
    if event:
        flash('Deletion of account successful.', category='success')

        logging.info("Logging out user and redirecting to home page")
        logout_user()
    else:
        flash('Error in deleting account.' , category='error')



    return redirect(url_for('views.home'))

@views.route('/follow/<handle>', methods=['GET'])
@login_required
def make_follower(handle):
    logging.info("User %s request to become follower of %s", current_user.handle, handle)
    
    current =time.time()
    is_follower = db_is_follower(website.db, website.dbConn, current_user.handle, handle)
    next = time.time()
    logging.info('Timing Plot is follower: %lf', next-current)
    
    assert not is_follower
    
    current = time.time()
    event = db_make_follower(website.db, website.dbConn, current_user.handle, handle)
    next = time.time()
    logging.info('Timing Plot make follower: %lf', next-current)
    
    if event:
        flash('You have become a follower of ' + handle, category='success')
    else:
        flash('Some error occured' + handle, category='error')

    return jsonify({})

@views.route('/unfollow/<handle>', methods=['GET'])
@login_required
def make_unfollower(handle):
    logging.info("User %s request to unfollower of %s", current_user.handle, handle)
    
    is_follower = db_is_follower(website.db, website.dbConn, current_user.handle, handle)
    assert is_follower
    
    current = time.time()
    event = db_make_unfollower(website.db, website.dbConn, current_user.handle, handle)
    next = time.time()
    logging.info('Timing Plot make unfollower: %lf', next-current)
    
    if event:
        flash('You have unfollowed ' + handle, category='success')
    else:
        flash('Some error occured' + handle, category='error')

    return jsonify({})

@views.route('/contest/<id>/problem/<index>', methods=['GET', 'POST'])
def problem(id, index):
    handle_upcoming_contests()

    if request.method == 'POST':
        if current_user.is_authenticated:
            handle_submission(id, index,  current_user.handle, request.form.get('Language') )
            return redirect(url_for('views.submissions', id=id))
        else:
            flash("You are not authorization", category='error')
            

    logging.info("Problem with index: %s in contest: %d is requested", index, int(id))

    current = time.time()
    contest = db_get_contest(website.db, website.dbConn, int(id))
    next = time.time()
    logging.info('Timing Plot Get contest: %lf', next-current)
    
    if contest == None:
        return redirect(url_for('views.home'))

    current = time.time()
    problem = db_get_problem(website.db, website.dbConn, int(id), index)
    next = time.time()
    logging.info('Timing Plot get problems: %lf', next-current)
    
    if problem == None:
        #TODO redirect to contest
        return redirect(url_for('views.home'))

    return render_template("problem.html", problem = website.Problem(problem), user=current_user, contest = website.Contest(contest))

@views.route('/contests')
def contestlist():
    handle_upcoming_contests()
    logging.info("Contest page is requested")
    ongoing_contests = db_get_ongoing_contests(website.db, website.dbConn)
    for (idx,contest) in enumerate(ongoing_contests):
        ongoing_contests[idx] = website.Contest(contest)

    curr_page = request.args.get('pageNo', default=1, type=int)
    contest_per_page = int(website.parser['contest']['contest_per_page'])

    first_page = (curr_page == 1)
    last_page = False
    current = time.time()
    finished_contests = db_get_finished_contests(website.db, website.dbConn, (curr_page-1)*contest_per_page, contest_per_page+1)
    next = time.time()
    logging.info('Timing Plot finished contest: %lf', next-current)
    
    if len(finished_contests) != contest_per_page + 1:
        last_page = True
    else:
        finished_contests.pop()

    for (idx,contest) in enumerate(finished_contests):
        finished_contests[idx] = website.Contest(contest)

    current =time.time()
    upcoming_contests = db_get_upcoming_contests(website.db,website.dbConn)
    next = time.time()
    logging.info('Timing Plot Get upcoming contest: %lf', next-current)
    
    for (idx,contest) in enumerate(upcoming_contests):
        upcoming_contests[idx] = website.Contest(contest)

    recent_contests = []
    if current_user.is_authenticated:
        current = time.time()
        recent_contests = db_get_recent_contests(website.db, website.dbConn, current_user.handle)
        next = time.time()
        logging.info('Timing Plot get recent ocntest: %lf', next-current)
    
        for (idx, contest) in enumerate(recent_contests):
            recent_contests[idx] = website.Contest(contest)
    
    return render_template("contests.html", user=current_user, ongoing_contests=ongoing_contests, finished_contests=finished_contests, upcoming_contests=upcoming_contests, recent_contests=recent_contests,  first_page=first_page, last_page=last_page, curr_page=curr_page)

@views.route('/contest/<contestId>', methods=['GET','POST'])
@login_required
def contest_home(contestId):
    handle_upcoming_contests()
    problem_list = []
    if request.method == 'POST':
        logging.info('Received File Input ')
        f = request.files['file']
        #f.save(secure_filename(f.filename))
        logging.info('Received File Name: '+ f.filename)
        #TODO: implement submission
    else:
        current = time.time()
        contest = db_get_contest_info(website.db, website.dbConn, contestId)
        contest_problems = db_get_contest_data(website.db, website.dbConn, contestId)
        next = time.time()
        logging.info('Timing Plot contest info and data: %lf', next-current)
    
        for (idx,problem) in enumerate(contest_problems):
            contest_problems[idx] = website.Problem(problem)


    return render_template("contest_home.html", user = current_user, contest = website.Contest(contest) , contest_problems = contest_problems)

@views.route('/create-contest', methods=['GET', 'POST'])
@login_required
def create_contest():
    if current_user.handle != "col362_ta":
        flash('You are not authorized to create contests', category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        start_after = request.form.get('start_after', default=0, type = int)
        duration = request.form.get('duration', default=120, type = int)
        contest_name = request.form.get('contest_name')

        problems = []

        for c_x in range(0, 20):
            c = chr( ord('A') + c_x)

            rating_c = request.form.get('rating' + c, default=-1, type=int)

            if rating_c == -1:
                break

            name_c = request.form.get('name'+c, default="", type=str)

            f_c = request.files['file'+c]

            points_c = request.form.get('points'+c, default=-1, type=int)
            tags_c = request.form.getlist('tags'+c) 
            problems.append((c, rating_c, name_c, f_c, points_c, tags_c) )

        contest_id = db_get_mx_contest_id(website.db, website.dbConn)
        if contest_id == None:
            flash("Creating contest unsuccesful", category = 'error')
            return redirect(url_for('views.contestlist'))
        
        contest_id += 1
        start_time = datetime.now() + timedelta(minutes=start_after) 

        current = time.time()
        event = db_create_contest(website.db, website.dbConn, contest_id,  contest_name, duration, start_time, problems )
        next = time.time()
        logging.info('Timing Plot Create contest: %lf', next-current)
    
        if not event:
            flash("Creating contest unsuccesful", category = 'error')
            return redirect(url_for('views.contestlist'))

        for problem in problems:
            filename = problem[3].filename
            file_ext = os.path.splitext(filename)[1]
            if file_ext != '.jpeg' and file_ext != '.jpg' and file_ext != '.png':
                flash("Invalid submission format", category = 'error')
                return redirect(url_for('views.contestlist'))
            directory = 'website/static/problemSet/' + str(contest_id)
            if not os.path.exists(directory):
                os.makedirs(directory)
            problem[3].save('website/static/problemSet/' + str(contest_id) + '/' + problem[0] + file_ext )


        return redirect(url_for('views.contestlist'))
        

    all_tags = db_get_all_problem_tags(website.db, website.dbConn)
    return render_template('create_contest.html', user=current_user, all_tags = all_tags)

@views.route('/contest/<id>/submissions', methods=['GET'])
@login_required
def submissions(id):

    all_submissions = db_get_submissions(website.db, website.dbConn, id, current_user.handle)
    contest = db_get_contest_info(website.db, website.dbConn, id)

    for (idx,submission) in enumerate(all_submissions):
        all_submissions[idx] = website.Submission(submission)

    return render_template('submissions.html', submissions=all_submissions, user=current_user, contest=website.Contest(contest))


def handle_upcoming_contests():
    upcoming_contest = db_get_upcoming_contests(website.db,website.dbConn)
    

    for contest in upcoming_contest:
        contest = website.Contest(contest)
        if contest.contestDate < datetime.now():
            db_change_contest_to_running(website.db, website.dbConn, contest.contestId)


    ongoing_contests = db_get_ongoing_contests(website.db, website.dbConn)
    print(ongoing_contests)
    for contest in ongoing_contests:
        contest = website.Contest(contest)
        if contest.contestDate + timedelta(minutes=contest.duration) < datetime.now():
            db_change_contest_to_finished(website.db, website.dbConn, contest.contestId)


#Blog Info

blog_store = dict()

@views.route('/blogs',methods=['GET'])
@login_required
def blogs():
    blogs_data = db_blogs_data(website.db, website.dbConn)
    return render_template('blog_list.html',blogs = blogs_data, user=current_user)


@views.route('blogs/<blogId>',methods=['GET'])
@login_required
def blogInfo(blogId):
    blogId = str(blogId)
    if blogId in blog_store:
        liked = 0
        if current_user.handle in blog_store[blogId].liked_by:
            liked = 1 
        reported = 0
        if current_user.handle in blog_store[blogId].reported_by:
            reported = 1
        return render_template('blog_page.html',blogData=blog_store[blogId], user = current_user, liked = liked, reported = reported)
    current = time.time()
    blogInfo = db_individual_blog(website.db, website.dbConn, blogId)
    next = time.time()
    logging.info('Timing Plot get blog: %lf', next-current)
    
    blog_store[blogId] = website.Blog(blogInfo[0])
    liked = 0
    if current_user.handle in blog_store[blogId].liked_by:
        liked = 1 
    reported = 0
    if current_user.handle in blog_store[blogId].reported_by:
        reported = 1
    return render_template('blog_page.html',blogData=blog_store[blogId], user = current_user, liked = liked, reported = reported)

@views.route('/contests/<contestId>/standing', methods=['GET'])
@login_required
def contest_standings(contestId):
    current = time.time()
    standings = db_contest_standings(website.db, website.dbConn, contestId)
    next = time.time()
    logging.info('Timing Plot Contest Standing: %lf', next-current)
    
    current = time.time()
    problem_list = db_individual_contest_data(website.db, website.dbConn, contestId)
    next = time.time()
    logging.info('Timing Plot Problem list: %lf', next-current)
    
    current = time.time()
    contest = db_individual_contest_info(website.db, website.dbConn, contestId)
    next = time.time()
    logging.info('Timing Plot Contest Info: %lf', next-current)
    
    problem_list.reverse()
    column = ['Standing', 'username', 'Points']
    rows = []
    problem_list.reverse()
    for problem in problem_list:
        column.append(problem[2])
    for users in standings:
        row = [users[2], users[1], users[3]]
        points_per_problems = ast.literal_eval(users[4])
        for points in points_per_problems:
            row.append(points[1])
        rows.append(row)
    logging.info(contest)
    logging.info(column)
    logging.info(rows)
    return render_template("contest_standings.html", contest = contest[0], user=current_user, column = column, rows = rows)

@views.route('blog/<blogId>/liked', methods=['GET','POST'])
@login_required
def like_blog(blogId):
    if blogId not in blog_store:
        blogInfo = db_individual_blog(website.db, website.dbConn, blogId)
        blog_store[blogId] = website.Blog(blogInfo[0])
    blogId = str(blogId)
    if current_user.handle in blog_store[blogId].liked_by:
        blog_store[blogId].like_count-=1
        blog_store[blogId].liked_by.remove(current_user.handle)
        author = website.User(db_get_user_with_handle(website.db, website.dbConn,blog_store[blogId].blogAuthor))
        current = time.time()
        status = db_update_contributions(website.db, website.dbConn, author.contribution-1, blog_store[blogId].blogAuthor)
        next = time.time()
        logging.info('Timing Plot Update COntributions: %lf', next-current)
    
        if status == 1:
            logging.info('Contribution Updated')
        else:
            logging.critical('Update Contribution Unsuccessful')
        reported = 0
        if current_user.handle in blog_store[blogId].reported_by:
            reported = 1
        return render_template('blog_page.html',blogData=blog_store[str(blogId)], user = current_user, liked = 0, reported_by = reported)
    blog_store[blogId].like_count+=1
    blog_store[blogId].liked_by.append(current_user.handle)
    author = website.User(db_get_user_with_handle(website.db, website.dbConn,blog_store[blogId].blogAuthor))
    status = db_update_contributions(website.db, website.dbConn, author.contribution+1,blog_store[blogId].blogAuthor)
    if status == 1:
        logging.info('Contribution Updated')
    else:
        logging.critical('Update Contribution Unsuccessful')
    reported = 0
    if current_user.handle in blog_store[blogId].reported_by:
        reported = 1
    return render_template('blog_page.html',blogData=blog_store[str(blogId)], user = current_user, liked = 1, reported = reported)


@views.route('blog/<blogId>/report', methods=['GET','POST'])
@login_required
def report_blog(blogId):
    if blogId not in blog_store:
        blogInfo = db_individual_blog(website.db, website.dbConn, blogId)
        blog_store[blogId] = website.Blog(blogInfo[0])
    blogId = str(blogId)
    if current_user.handle not in blog_store[blogId].reported_by:
        blog_store[blogId].report_count+=1
        blog_store[blogId].reported_by.append(current_user.handle)
        status = db_update_blog_reports(website.db, website.dbConn, blog_store[blogId].report_count, int(blogId))
        if status == 1:
            logging.info('Report Count Updated to %d!!!', blog_store[blogId].report_count)
        else:
            logging.critical('Report Count updated Failed!!!')
        liked = 0
        if current_user.handle in blog_store[blogId].liked_by:
            liked = 1
        return render_template('blog_page.html', blogData = blog_store[blogId], user = current_user, liked = liked, reported = 1)
    liked = 0
    if current_user.handle in blog_store[blogId].liked_by:
        liked = 1
    return render_template('blog_page.html', blogData = blog_store[blogId], user = current_user, liked = liked, reported = 1)
