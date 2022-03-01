import datetime

parser = None

db = None
dbConn = None

login_manager = None

# Maintained for integrity
# Attributes of user should be passed using this class
class User:
    def __init__(self, user, is_admin=False):
        (handle, firstname, lastname, country, rating, contribution, password) = user
        self.handle = handle
        self.is_admin = is_admin
        self.firstname = firstname
        self.lastname = lastname
        self.country = country
        self.rating = rating
        self.contribution = contribution
        self.password = password
        self.authenticated = False
        self.numfollowers = None #Note: only non None for profile function other always null
    
    def is_active(self):
        return True

    def get_id(self):
        return self.handle

    # def is_admin(self):
        # return self.admin

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False
    
    def getStr(self):
        return "('%s', '%s', '%s', '%s', %s, %s, '%s')" % (self.handle, self.firstname, self.lastname, self.country, self.rating, self.contribution, str(self.password))
        
class Problem:
    def __init__(self, problem):
        (name, contestId, problemIndex, rating, tags, points, url) = problem
        self.name = name
        self.contestId = contestId
        self.problemIndex = problemIndex
        self.rating = rating
        self.tags = tags
        self.points = points
        self.url = url

        self.correct_submissions = 0


class Contest:
    def __init__(self, contest):
        (contestId, contestName,  problems, status, duration, contestDate) = contest
        self.contestId = contestId
        self.contestName = contestName
        # self.contestDate = datetime.datetime(contestDate)
        self.problems = problems
        self.status = status
        self.duration = duration
        self.contestDate = datetime.datetime.strptime(str(contestDate), '%Y-%m-%d %H:%M:%S')
         
class Submission:
    def __init__(self, submission):
        (sid, cid, sType, pIdx, ath, pLan, ver, timeConsum, memebytes, sTime) = submission
        self.submissionId = sid
        self.contestId = cid
        self.submissionType = sType
        self.problemIndex = pIdx
        self.author = ath
        self.programmingLanguage = pLan
        self.verdict = ver
        self.timeconsumedmillis = timeConsum
        self.memoryconsumedbytes = memebytes
        self.submissionTime = sTime


    def getStr(self):
        return str(self.submissionId) + ','  + str(self.contestId) + ',\'' + str(self.submissionType) + '\',\'' + str(self.author) + '\',\'' + str(self.programmingLanguage) + '\',\'' + str(self.verdict) + '\',' + str(self.timeconsumedmillis) + ',' + str(self.memoryconsumedbytes) + ',\'' + str(self.problemIndex) + '\',' + 'CAST ( \'' + str(self.submissionTime) + '\' AS timestamp )'








        self.contestDate = contestDate



class Blog:
    def __init__(self, blog):
        (blogId,blogName,blogAuthor,comments) = blog
        self.blogId = blogId
        self.blogName = blogName
        self.blogAuthor = blogAuthor
        self.count_comments = comments
        self.like_count = 0
        self.liked_by = []
        self.report_count = 0
        self.reported_by = []
        
#Points to be noted 
#1. Database will return tuples
#2. If required tuples can be converted to the User class
#3. Database function doing insert will take these classes as input
