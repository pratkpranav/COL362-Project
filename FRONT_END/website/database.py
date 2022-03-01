import psycopg2
import logging
import os
import sys
import website
from website.sqlQueries import *

def get_database_connection(host, port, name, user, password):
    logging.info("Connecting to database...")

    try:
        dbConn = psycopg2.connect(host=host, database=name, user=user, password=password, port=port)
        db = dbConn.cursor()
        logging.info("Connected to Database!")
    except:
        error = sys.exc_info()[0]
        logging.error("Connection to database failed with error: " + str(error))
        sys.exit(-1)
    return db, dbConn


def close_database_connection(db, dbConn):
    logging.info("Closing connection to database")

    if db is not None:
        db.close()
        logging.info("Communication cursor closed.")
    else:
        logging.warning("Trying to close a connection with NULL cursor")

    if dbConn is not None:
        dbConn.close()
        logging.info("Connection closed.")
    else:
        logging.warning("Trying to close a connection with NULL connection")

def db_get_user_with_handle(db, dbConn, handle):
    # Returns the user with handle=handle if user exists, else returns None
    logging.info("Querying User with Handle %s:", handle)
    if handle == "":
        logging.warning("Querying user with empty handle")
        return None
    if db == None:
        logging.critical("Querying with None db cursor!!")
        return None

    user_query = sql_user_with_handle % {'handle':handle}
    logging.debug(user_query)

    try:
        db.execute(user_query) 
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical("Error querying the users table: %s",  e)
        dbConn.rollback()
        return None

    assert len(result) <= 1
    if len(result) == 1:
        return result[0]
    else:
        return None

def db_insert_user(db, dbConn, user):
    logging.info("Adding user: %s to users table", user.getStr() )
    assert len(user.handle) != 0
    assert len(user.firstname) != 0
    assert len(user.password) != 0

    if db == None:
        logging.critical("Inserting user with None db cursor!!")
        return 

    user_insert_query = sql_insert_user % {'user': user.getStr() }
    logging.debug("Insert query: %s", user_insert_query)
    try:
        db.execute(user_insert_query)
        dbConn.commit()
    except Exception as e:
        logging.critical("Error inserting in the users table: %s",  e)
        dbConn.rollback()
    else:
        logging.debug("Insert query into users tables was successful")

def db_update_user(db, dbConn, handle, new_user):
    logging.info("Updating user with handle: %s", handle)
    logging.debug("New user attributes: %s", new_user.getStr())

    if db == None:
        logging.critical("Updating user with None db cursor!!")
        return 

    user_update_query = sql_update_user % {'old_handle': handle, 'new_handle': new_user.handle, 'firstname': new_user.firstname, 'lastname': new_user.lastname, 'country': new_user.country, 'password': new_user.password }

    logging.debug("Update user query: %s", user_update_query)
    try:
        db.execute(user_update_query)
        dbConn.commit()
    except Exception as e:
        logging.critical("Error updating the users table: %s", e)
        dbConn.rollback()
    else:
        logging.info("Update query into users table was successful.")

def db_delete_user(db, dbConn, handle):
    logging.info("Deleteing user: %s", handle)

    if db == None:
        logging.critical("Updating user with None db cursor!!")
        return 

    user_delete_query = sql_delete_user % {'handle': handle}
    logging.debug("Delete user query: %s", user_delete_query)

    try:
        db.execute(user_delete_query)
        dbConn.commit()
    except Exception as e:
        logging.critical("Error deleting the user from users table: %s", e)
        dbConn.rollback()
        return False
    else:
        logging.info("Deleting user was successful.")
    return True

def db_get_top_rated_users(db, dbConn, num):
    assert num >= 0
    logging.info("Querying database for %d top rated users", num)

    if db == None:
        logging.critical("Updating user with None db cursor!!")
        return 
    
    user_top_rated_query = sql_top_x_rated_users % {'num': num }
    logging.debug("User top rated query: %s", user_top_rated_query)
    
    try:

        logging.info('creating view for top 100 rated users')
        db.execute(sql_create_view_top_x_rated_users)
    
    except Exception as e:
        dbConn.rollback()
        logging.info('View already exists!!')

    try: 
        logging.info('using top_users view for getting top rated users')
        db.execute(user_top_rated_query)
        result = db.fetchall()
        logging.debug(result)
        assert len(result) <= num
        dbConn.commit()
    except Exception as e:
        logging.critical("Error querying top rated users. Error: %s", e)
        dbConn.rollback()
        return []

    return result

def db_get_top_contributors_users(db, dbConn, num):
    assert num >= 0
    logging.info("Querying database for %d top contributors users", num)

    if db == None:
        logging.critical("Updating user with None db cursor!!")
        return 
    
    user_top_contributors_query = sql_top_x_contributors_users % {'num': num }
    logging.debug("User top contributors query: %s", user_top_contributors_query)
    try: 
        db.execute(user_top_contributors_query)
        result = db.fetchall()
        logging.debug(result)
        assert len(result) <= num
        dbConn.commit()
    except Exception as e:
        logging.critical("Error querying top rated users. Error: %s", e)
        dbConn.rollback()
        return []

    return result

def db_get_countries(db, dbConn):
    logging.info("Querying database for coutries name")

    if db == None:
        logging.critical("Updating user with None db cursor!!")
        return 
    
    countries_query = sql_countries 
    logging.debug("Sql query for countries: %s", countries_query)

    try:
        db.execute(countries_query)
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical("Error querying countries with prefix. Error %s", e)
        dbConn.rollback()
        return []
    return result


#TODO: complete function when more tables are added
def db_get_users_with(db, dbConn, country, handle, rcmp, rating, cntrcmp, contribution, fcmp, numfollowers, cnstcmp, numcontests, offset, length ):
    logging.info("Querying database for users with provided attributes")
    logging.debug("Handle: %s", handle)
    logging.debug("Country: %s", country)
    logging.debug("Rating: %s", rating)
    logging.debug("Contributions: %s", contribution)
    logging.debug("Numfriends: %s", numfollowers)
    logging.debug("Numcontest: %s", numcontests)
    logging.debug("rcmp: %s, cntrcmp: %s, fcmp: %s, cnstcmp: %s", rcmp, cntrcmp, fcmp, cnstcmp)
    
    cmp_to_op = { 'ge': '>=', 'gt': '>', 'lt': '<', 'le': '<='}

    def transform_handle(handle):
        t_handle = "%"
        for c in handle:
            t_handle += c
            t_handle += '%'
        return t_handle
    if country == "":
        country = "%"
    
    users_query = sql_users % {'handle': transform_handle(handle), 'rop': cmp_to_op[rcmp], 'cntrop': cmp_to_op[cntrcmp], 'rating': rating, 'contribution': contribution, 'country': country, 'numfollowers': numfollowers, 'fcmp': cmp_to_op[fcmp], 'length':length, 'offset': offset}
    try:
        logging.debug("Users search query: %s", users_query)
        db.execute(users_query)
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical("Error querying database for users. Error %s", e)
        dbConn.rollback()
        return []
    return result

def db_get_num_followers(db, dbConn, handle):
    logging.info("Querying #num of followers of %s", handle)

    user_num_friend_query = sql_num_followers % {'handle1': handle}

    try:
        db.execute(user_num_friend_query)
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical("Error querying database for friends of %s", handle)
        dbConn.rollback()
        return 0
    return result[0][0]
    

def db_is_follower(db, dbConn, handle1, handle2):

    logging.info("Check if %s is a follower of %s", handle1, handle2)
    user_follower_query = sql_check_follower % {'handle1': handle1, 'handle2': handle2}
    logging.debug("Query: %s", user_follower_query)
    try:
        db.execute(user_follower_query)
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical("Error querying database when checking follower. Error %s", e)
        dbConn.rollback()
        return False
    assert len(result) <= 1
    return (len(result) == 1)

def db_make_follower(db, dbConn, handle1, handle2):
    logging.info("Inserting into friends table: (%s, %s)", handle1, handle2)
    user_make_follower_query = sql_make_follower % {'handle1': handle1, 'handle2': handle2}
    logging.debug("Query: %s", user_make_follower_query)

    try:
        db.execute(user_make_follower_query)
        dbConn.commit()
    except Exception as e:
        logging.critical("Inserting into friends table unsuccesful. Error %s", e)
        dbConn.rollback()
        return False
    else:
        logging.info("Insertion is successful")
    return True

def db_make_unfollower(db, dbConn, handle1, handle2):
    logging.info("Deleting from friends table: (%s, %s)", handle1, handle2)
    user_make_unfollower_query = sql_make_unfollower % {'handle1': handle1, 'handle2': handle2}
    logging.debug("Query: %s", user_make_unfollower_query)

    try:
        db.execute(user_make_unfollower_query)
        dbConn.commit()
    except Exception as e:
        logging.critical("Deleting from friends table unsuccesful. Error %s", e)
        dbConn.rollback()
        return False
    else:
        logging.info("Deletion is successful")
    return True

def db_get_all_problem_tags(db, dbConn):
    logging.info("Querying database for all tags")
    problem_all_tag_query = sql_get_tags 
    logging.debug("Query %s", problem_all_tag_query)

    try:
        db.execute(problem_all_tag_query)
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical("Fetching tags unsuccesful. Error %s", e)
        dbConn.rollback()
        return []
    else:
        logging.info("Fetching tags successful")
    return result[0][0]

def db_get_problems_with(db, dbConn, rating, rcmp, tags, offset, length):
    logging.info("Querying database for problems with provided attributes")
    logging.debug("Rating: %s", rating)
    logging.debug("Rcmp: %s", rcmp)
    logging.debug("Tags: [")
    for tag in tags:
        logging.debug("%s,", tag)
    logging.debug("]")
    logging.debug("Offset: %s", offset)
    logging.debug("Length: %s", length)
    cmp_to_op = { 'ge': '>=', 'gt': '>', 'lt': '<', 'le': '<='}

    if '' in tags:
        tags.remove('') #remove this if present
    if len(tags) > 0:
        problem_search_query = sql_search_problems % {'rating':rating, 'rop':cmp_to_op[rcmp], 'ptags':str(tags), 'length':length, 'offset':offset }
    else:
        problem_search_query = sql_search_problems_without_tags % {'rating':rating, 'rop':cmp_to_op[rcmp], 'length':length, 'offset':offset }
    logging.debug(problem_search_query)
    try:
        db.execute(problem_search_query)
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical('Fetching problems was unsuccesful. Error %s', e)
        dbConn.rollback()
        return []
    else:
        logging.info('Fetching problems successful')
    return result
        
def db_get_num_followers(db, dbConn, handle):
    logging.info("Querying #num of followers of %s", handle)

    user_num_friend_query = sql_num_followers % {'handle1': handle}

    try:
        db.execute(user_num_friend_query)
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical("Error querying database for friends of %s", handle)
        dbConn.rollback()
        return 0
    return result[0][0]
    

def db_is_follower(db, dbConn, handle1, handle2):

    logging.info("Check if %s is a follower of %s", handle1, handle2)
    user_follower_query = sql_check_follower % {'handle1': handle1, 'handle2': handle2}
    logging.debug("Query: %s", user_follower_query)
    try:
        db.execute(user_follower_query)
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical("Error querying database when checking follower. Error %s", e)
        dbConn.rollback()
        return False
    assert len(result) <= 1
    return (len(result) == 1)

def db_make_follower(db, dbConn, handle1, handle2):
    logging.info("Inserting into friends table: (%s, %s)", handle1, handle2)
    user_make_follower_query = sql_make_follower % {'handle1': handle1, 'handle2': handle2}
    logging.debug("Query: %s", user_make_follower_query)

    try:
        db.execute(user_make_follower_query)
        dbConn.commit()
    except Exception as e:
        logging.critical("Inserting into friends table unsuccesful. Error %s", e)
        dbConn.rollback()
        return False
    else:
        logging.info("Insertion is successful")
    return True

def db_make_unfollower(db, dbConn, handle1, handle2):
    logging.info("Deleting from friends table: (%s, %s)", handle1, handle2)
    user_make_unfollower_query = sql_make_unfollower % {'handle1': handle1, 'handle2': handle2}
    logging.debug("Query: %s", user_make_unfollower_query)

    try:
        db.execute(user_make_unfollower_query)
        dbConn.commit()
    except Exception as e:
        logging.critical("Deleting from friends table unsuccesful. Error %s", e)
        dbConn.rollback()
        return False
    else:
        logging.info("Deletion is successful")
    return True

def db_get_all_problem_tags(db, dbConn):
    logging.info("Querying database for all tags")
    problem_all_tag_query = sql_get_tags 
    logging.debug("Query %s", problem_all_tag_query)

    try:
        db.execute(problem_all_tag_query)
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical("Fetching tags unsuccesful. Error %s", e)
        dbConn.rollback()
        return []
    else:
        logging.info("Fetching tags successful")
    return result[0][0]

def db_get_problems_with(db, dbConn, rating, rcmp, tags, offset, length):
    logging.info("Querying database for problems with provided attributes")
    logging.debug("Rating: %s", rating)
    logging.debug("Rcmp: %s", rcmp)
    logging.debug("Tags: [")
    for tag in tags:
        logging.debug("%s,", tag)
    logging.debug("]")
    logging.debug("Offset: %s", offset)
    logging.debug("Length: %s", length)
    cmp_to_op = { 'ge': '>=', 'gt': '>', 'lt': '<', 'le': '<='}

    if '' in tags:
        tags.remove('') #remove this if present
    if len(tags) > 0:
        problem_search_query = sql_search_problems % {'rating':rating, 'rop':cmp_to_op[rcmp], 'ptags':str(tags), 'length':length, 'offset':offset }
    else:
        problem_search_query = sql_search_problems_without_tags % {'rating':rating, 'rop':cmp_to_op[rcmp], 'length':length, 'offset':offset }
    logging.debug(problem_search_query)
    try:
        db.execute(problem_search_query)
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical('Fetching problems was unsuccesful. Error %s', e)
        dbConn.rollback()
        return []
    else:
        logging.info('Fetching problems successful')
    return result
        

    return result

def db_get_num_followers(db, dbConn, handle):
    logging.info("Querying #num of followers of %s", handle)

    user_num_friend_query = sql_num_followers % {'handle1': handle}

    try:
        db.execute(user_num_friend_query)
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical("Error querying database for friends of %s", handle)
        dbConn.rollback()
        return 0
    return result[0][0]
    

def db_is_follower(db, dbConn, handle1, handle2):

    logging.info("Check if %s is a follower of %s", handle1, handle2)
    user_follower_query = sql_check_follower % {'handle1': handle1, 'handle2': handle2}
    logging.debug("Query: %s", user_follower_query)
    try:
        db.execute(user_follower_query)
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical("Error querying database when checking follower. Error %s", e)
        dbConn.rollback()
        return False
    assert len(result) <= 1
    return (len(result) == 1)

def db_make_follower(db, dbConn, handle1, handle2):
    logging.info("Inserting into friends table: (%s, %s)", handle1, handle2)
    user_make_follower_query = sql_make_follower % {'handle1': handle1, 'handle2': handle2}
    logging.debug("Query: %s", user_make_follower_query)

    try:
        db.execute(user_make_follower_query)
        dbConn.commit()
    except Exception as e:
        logging.critical("Inserting into friends table unsuccesful. Error %s", e)
        dbConn.rollback()
        return False
    else:
        logging.info("Insertion is successful")
    return True

def db_make_unfollower(db, dbConn, handle1, handle2):
    logging.info("Deleting from friends table: (%s, %s)", handle1, handle2)
    user_make_unfollower_query = sql_make_unfollower % {'handle1': handle1, 'handle2': handle2}
    logging.debug("Query: %s", user_make_unfollower_query)

    try:
        db.execute(user_make_unfollower_query)
        dbConn.commit()
    except Exception as e:
        logging.critical("Deleting from friends table unsuccesful. Error %s", e)
        dbConn.rollback()
        return False
    else:
        logging.info("Deletion is successful")
    return True

def db_get_all_problem_tags(db, dbConn):
    logging.info("Querying database for all tags")
    problem_all_tag_query = sql_get_tags 
    logging.debug("Query %s", problem_all_tag_query)

    try:
        db.execute(problem_all_tag_query)
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical("Fetching tags unsuccesful. Error %s", e)
        dbConn.rollback()
        return []
    else:
        logging.info("Fetching tags successful")
    return result[0][0]

def db_get_problems_with(db, dbConn, rating, rcmp, tags, offset, length):
    logging.info("Querying database for problems with provided attributes")
    logging.debug("Rating: %s", rating)
    logging.debug("Rcmp: %s", rcmp)
    logging.debug("Tags: [")
    for tag in tags:
        logging.debug("%s,", tag)
    logging.debug("]")
    logging.debug("Offset: %s", offset)
    logging.debug("Length: %s", length)
    cmp_to_op = { 'ge': '>=', 'gt': '>', 'lt': '<', 'le': '<='}

    if '' in tags:
        tags.remove('') #remove this if present
    if len(tags) > 0:
        problem_search_query = sql_search_problems % {'rating':rating, 'rop':cmp_to_op[rcmp], 'ptags':str(tags), 'length':length, 'offset':offset }
    else:
        problem_search_query = sql_search_problems_without_tags % {'rating':rating, 'rop':cmp_to_op[rcmp], 'length':length, 'offset':offset }
    logging.debug(problem_search_query)
    try:
        db.execute(problem_search_query)
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical('Fetching problems was unsuccesful. Error %s', e)
        dbConn.rollback()
        return []
    else:
        logging.info('Fetching problems successful')
    return result
        

    return result

def db_get_num_followers(db, dbConn, handle):
    logging.info("Querying #num of followers of %s", handle)

    user_num_friend_query = sql_num_followers % {'handle1': handle}

    try:
        db.execute(user_num_friend_query)
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical("Error querying database for friends of %s", handle)
        dbConn.rollback()
        return 0
    return result[0][0]
    

def db_is_follower(db, dbConn, handle1, handle2):

    logging.info("Check if %s is a follower of %s", handle1, handle2)
    user_follower_query = sql_check_follower % {'handle1': handle1, 'handle2': handle2}
    logging.debug("Query: %s", user_follower_query)
    try:
        db.execute(user_follower_query)
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical("Error querying database when checking follower. Error %s", e)
        dbConn.rollback()
        return False
    assert len(result) <= 1
    return (len(result) == 1)

def db_make_follower(db, dbConn, handle1, handle2):
    logging.info("Inserting into friends table: (%s, %s)", handle1, handle2)
    user_make_follower_query = sql_make_follower % {'handle1': handle1, 'handle2': handle2}
    logging.debug("Query: %s", user_make_follower_query)

    try:
        db.execute(user_make_follower_query)
        dbConn.commit()
    except Exception as e:
        logging.critical("Inserting into friends table unsuccesful. Error %s", e)
        dbConn.rollback()
        return False
    else:
        logging.info("Insertion is successful")
    return True

def db_make_unfollower(db, dbConn, handle1, handle2):
    logging.info("Deleting from friends table: (%s, %s)", handle1, handle2)
    user_make_unfollower_query = sql_make_unfollower % {'handle1': handle1, 'handle2': handle2}
    logging.debug("Query: %s", user_make_unfollower_query)

    try:
        db.execute(user_make_unfollower_query)
        dbConn.commit()
    except Exception as e:
        logging.critical("Deleting from friends table unsuccesful. Error %s", e)
        dbConn.rollback()
        return False
    else:
        logging.info("Deletion is successful")
    return True

def db_get_all_problem_tags(db, dbConn):
    logging.info("Querying database for all tags")
    problem_all_tag_query = sql_get_tags 
    logging.debug("Query %s", problem_all_tag_query)

    try:
        db.execute(problem_all_tag_query)
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical("Fetching tags unsuccesful. Error %s", e)
        dbConn.rollback()
        return []
    else:
        logging.info("Fetching tags successful")
    return result[0][0]

def db_get_problems_with(db, dbConn, rating, rcmp, tags, offset, length):
    logging.info("Querying database for problems with provided attributes")
    logging.debug("Rating: %s", rating)
    logging.debug("Rcmp: %s", rcmp)
    logging.debug("Tags: [")
    for tag in tags:
        logging.debug("%s,", tag)
    logging.debug("]")
    logging.debug("Offset: %s", offset)
    logging.debug("Length: %s", length)
    cmp_to_op = { 'ge': '>=', 'gt': '>', 'lt': '<', 'le': '<='}

    if '' in tags:
        tags.remove('') #remove this if present
    if len(tags) > 0:
        problem_search_query = sql_search_problems % {'rating':rating, 'rop':cmp_to_op[rcmp], 'ptags':str(tags), 'length':length, 'offset':offset }
    else:
        problem_search_query = sql_search_problems_without_tags % {'rating':rating, 'rop':cmp_to_op[rcmp], 'length':length, 'offset':offset }
    logging.debug(problem_search_query)
    try:
        db.execute(problem_search_query)
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical('Fetching problems was unsuccesful. Error %s', e)
        dbConn.rollback()
        return []
    else:
        logging.info('Fetching problems successful')
    return result
       
def db_get_problem(db, dbConn, contestId, index):
    logging.info("Fetching problem with index: %s in contest: %d form database", index, contestId)

    get_problem_query = sql_get_problem % {'index': index, 'contestId': contestId}
    logging.debug("Query %s", get_problem_query)
    try:
        db.execute(get_problem_query)
        result = db.fetchall()
        assert(len(result) <= 1)
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical("Error fetching problem from database. Error %s", e)
        dbConn.rollback()
        return None
    else:
        logging.info("Fetching problem successful")

    if len(result) == 0:
        return None
    return result[0]

def db_get_contest(db, dbConn, id):
    logging.info('Fetching contest with id: %d', id)
    
    get_contest_query = sql_get_contest % {'contestId': id}
    logging.debug("Query: %s", get_contest_query)

    try:
        db.execute(get_contest_query)
        result = db.fetchall()
        assert len(result) <= 1
        # logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical('Error fetching contest from database. Error %s', e)
        dbConn.rollback()
        return None
    else:
        logging.info('Fetching contest successful')

    if len(result) == 0:
        return None
    return result[0]


def db_get_ongoing_contests(db, dbConn):
    logging.info("Fetching ongoing contests")
    ongoing_contests_query = sql_get_ongoing_contests
    logging.debug("Query: %s", ongoing_contests_query)

    try:
        db.execute(ongoing_contests_query)
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical('Error fetching ongoing contests. Error %s', e)
        dbConn.rollback()
        return []
    else:
        logging.info('Fetching ongoing contests successful')

    return result

def db_get_upcoming_contests(db, dbConn):
    logging.info("Fetching upcoming contests")
    upcoming_contests_query = sql_get_upcoming_contests
    logging.debug("Query: %s", upcoming_contests_query)

    try:
        db.execute(upcoming_contests_query)
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical('Error fetching ongoing contests. Error %s', e)
        dbConn.rollback()
        return []
    else:
        logging.info('Fetching ongoing contests successful')

    return result

def db_get_finished_contests(db, dbConn, offset, length):
    logging.info("Fetching finished contests")
    finished_contests_query = sql_get_finished_contests % {'offset': offset, 'length': length}
    logging.debug("Query %s", finished_contests_query)

    try:
        db.execute(finished_contests_query)
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical('Error fetching finished contests. Error %s', e)
        return []

    return result

def db_get_recent_contests(db, dbConn, handle):
    logging.info("Fetching contests with recent submission")
    recent_contests_query = sql_get_recent_contests % {'handle': handle}
    logging.debug("Query: %s", recent_contests_query)

    return []
    try:
        db.execute(recent_contests_query)
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical("Error fetching contests with recent submission. Error %s", e)
        dbConn.rollback()
        return []


    return result


def db_get_contest_info(db,dbConn,contestId):
    logging.info("Fetching contest data for id: %s", contestId)
    get_contest_query = sql_get_contest % {'contestId': int(contestId)}
    logging.debug("Query: %s", get_contest_query)
    try:
        db.execute(get_contest_query)
        result = db.fetchall()
        assert len(result) <= 1
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical("Fetchig contest info unsuccesful. Error %s", e)
        dbConn.rollback()
        return []
    else:
        logging.info("Fetching contest info successful")

    if len(result) == 0:
        return None
    
    return result[0]


def db_get_contest_data(db,dbConn,contestId):
    logging.info("Fetching contest data for id: %s", contestId)
    contest_data_query = sql_get_contest_data % {'contestId': int(contestId)}

    logging.debug("Query: %s", contest_data_query)
    try:
        db.execute(contest_data_query)
        result = db.fetchall()
        dbConn.commit()
    except Exception as e:
        logging.critical("Fetching contest data unsuccesful. Error %s", e)
        dbConn.rollback()
        return []
    else:
        logging.info("Fetching contest data successful")
    
    return result

def db_get_mx_contest_id(db, dbConn):
    logging.info("Fetching max contest id")
    max_contest_id_query = sql_get_max_contest_id
    logging.debug("Query: %s", max_contest_id_query)

    try:
        db.execute(max_contest_id_query)
        result = db.fetchall()
        logging.debug(result)
        dbConn.commit()
    except Exception as e:
        logging.critical("Fetching max contest id unsuccesful. Error %s", e)
        dbConn.rollback()
        return None
    else:
        logging.info("Fetching max contest id successful")
    assert len(result) == 1

    return result[0][0]


def db_create_contest(db, dbConn, contestId, contestName, duration, contestDate, problems):
    logging.info("Creating new contest")
    logging.debug(problems)
    curr = contestDate.strftime('%Y-%m-%d %H:%M:%S')
    p_list = []
    for p in problems:
        p_list.append(p[0])
    logging.debug(p)

    create_contest_query = sql_create_contest % {'contestId': contestId, 'contestName': contestName, 'problems': str(p_list), 'duration': duration, 'contestDate': curr}
    logging.debug(create_contest_query)

    create_problems_query = []
    for problem in problems:
        filename = problem[3].filename
        frmt = os.path.splitext(filename)[1]
        url = 'problemSet/' + str(contestId) + '/' + problem[0] + frmt
        create_problem_query = sql_create_problem % {'name': problem[2], 'contest_id': contestId, 'problemIndex': problem[0], 'rating': problem[1], 'tags': str(problem[5]), 'url':  url, 'points': problem[4] }
        create_problems_query.append(create_problem_query)
        logging.debug(create_problem_query)

    try:
        db.execute(create_contest_query)
        for create_problem_query in create_problems_query:
            db.execute(create_problem_query)
        dbConn.commit()
    except Exception as e:
        logging.critical("Creating contest failed. Error %e", e)
        return False
    else:
        logging.info("Creating contest successful")

    return True

def db_change_contest_to_running(db, dbConn, contestId):
    logging.info("Making contest: %d running", contestId)

    make_contest_running_query = sql_make_contest_running % {'contestId': contestId}
    logging.debug(make_contest_running_query)

    try:
        db.execute(make_contest_running_query)
        dbConn.commit()
    except Exception as e:
        logging.critical('Failed to make contest runnable. Error %e', e)
        dbConn.rollback()
    else:
        logging.info("Made contest runnable")

def db_change_contest_to_finished(db, dbConn, contestId):
    logging.info("Make contest: %d finished", contestId)
    make_contest_finished_query = sql_make_contest_finished % {'contestId': contestId}

    logging.debug(make_contest_finished_query)

    try:
        db.execute(make_contest_finished_query)
        dbConn.commit()
    except Exception as e:
        logging.critical('Failed to finish contest. Error %e', e)
        dbConn.rollback()
    else:
        logging.info("Made contest finished")


def db_get_submissions(db, dbConn, id, handle):
    logging.info("Getting submissions %d, %s", int(id), handle)

    submissions_query = sql_get_submissions % {'contestId': int(id), 'handle': handle}
    logging.debug(submissions_query)

    try:
        db.execute(submissions_query)
        result = db.fetchall()
        dbConn.commit()
    except Exception as e:
        logging.critical("Failed getting submissions. Error %s", e)
        dbConn.rollback()
    else:
        logging.info("Successful getting submissions")

    return result


def db_add_submission(db, dbConn, sub):
    logging.info("Adding submission to table")

    add_submission_query = sql_add_submission % {'values': sub.getStr()} 
    logging.debug(add_submission_query)

    try:
        db.execute(add_submission_query)
        dbConn.commit()
    except Exception as e:
        logging.critical("Failed adding submission. Error %s", e)
        dbConn.rollback()
    else:
        logging.info("Successful adding submission")



def db_blogs_data(db,dbConn):
    blogs_list = sql_blogs_list 
    try:
        db.execute(blogs_list)
        result = db.fetchall()
        dbConn.commit()
    except Exception as e:
        logging.critical("Fetching blogs data unsuccesful. Error %s", e)
        dbConn.rollback()
        return []
    else:
        logging.info("Fetching blogs data successful")
    
    return result

def db_individual_blog(db,dbConn,blogId):
    blog = sql_blog_fetch % {'blogId': int(blogId)}
    try:
        db.execute(blog)
        result = db.fetchall()
        dbConn.commit()
    except Exception as e:
        logging.critical("Fetching individual blog data unsuccessful. Error %s", e)
        dbConn.rollback()
        return []
    else:
        logging.info("Fetching individual blog data successful")
    
    return result
    

def db_top_blogs(db,dbConn):
    blogs = sql_top_blogs
    try:
        db.execute(blogs)
        result = db.fetchall()
        dbConn.commit()
    except Exception as e:
        logging.critical("Fetching top blogs unsuccessful. Error %s", e)
        dbConn.rollback()
        return []
    else:
        logging.info("Fetching top blogs successful")
    
    return result



def db_contest_standings(db,dbConn,contestId):
    standings = sql_contest_standing % {'contestId': int(contestId)}
    try:
        db.execute(standings)
        result = db.fetchall()
        dbConn.commit()
    except Exception as e:
        logging.critical("Fetching contest standings unsuccesful. Error %s", e)
        dbConn.rollback()
        return []
    else:
        logging.info("Fetching contest standings successful")
    
    return result

def db_individual_contest_info(db,dbConn,contestId):
    contest = sql_contest_info_individual % {'contestId': int(contestId)}
    try:
        db.execute(contest)
        result = db.fetchall()
        dbConn.commit()
    except Exception as e:
        logging.critical("Fetching contest info unsuccesful. Error %s", e)
        dbConn.rollback()
        return []
    else:
        logging.info("Fetching contest info successful")
    
    return result


def db_individual_contest_data(db,dbConn,contestId):
    contest = sql_contest_data_individual % {'contestId': int(contestId)}
    try:
        db.execute(contest)
        result = db.fetchall()
        dbConn.commit()
    except Exception as e:
        logging.critical("Fetching contest data unsuccesful. Error %s", e)
        dbConn.rollback()
        return []
    else:
        logging.info("Fetching contest data successful")
    
    return result

def db_update_contributions(db,dbConn,contribution,handle):
    update = sql_update_contributions % {'contribution': contribution, 'handle': handle}
    try:
        db.execute(update)
        # result = db.fetchall()
        dbConn.commit()
    except Exception as e:
        logging.debug(update)
        logging.critical("Fetching update user contribution unsuccesful. Error %s", e)
        dbConn.rollback()
        return -1
    else:
        logging.info("Fetching update user contribution successful")
    
    return 1

def db_update_blog_reports(db, dbConn, report_count, blogId):
    report_blog = sql_update_blog_reports % {'report_count' : report_count, 'blogId': blogId}
    try:
        db.execute(report_blog)
        dbConn.commit()
    except Exception as e:
        logging.debug(report_blog)
        logging.critical("Update blog report count unsuccesful. Error %s", e)
        dbConn.rollback()
        return -1
    else:
        logging.info("Update blog report count successful")

    return 1

def db_blog_delete_triggers(db, dbConn):
    report_function = sql_report_trigger
    report_trigger = sql_create_report_trigger
    try:
        db.execute(report_function)
        dbConn.commit()
    except Exception as e:
        logging.debug(report_function)
        logging.critical("Report function addition unsuccessful. Error %s", report_function)
        return -1
    else:
        logging.info("Report function addition successful")
    
    try:
        db.execute(report_trigger)
        dbConn.commit()
    except Exception as e:
        logging.debug(report_function)
        logging.critical("Report trigger addition unsuccessful. Error %s", report_function)
        return -1
    else:
        logging.info("Report trigger addition successful")
    return 1