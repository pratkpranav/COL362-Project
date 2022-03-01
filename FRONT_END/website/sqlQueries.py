

sql_user_with_handle = """
                        SELECT *
                        FROM users
                        WHERE users.handle = '%(handle)s';
                   """

sql_insert_user = """
                    INSERT INTO users VALUES %(user)s;
                  """


sql_update_user = """
                        UPDATE users
                        SET handle = '%(new_handle)s', firstname = '%(firstname)s', lastname = '%(lastname)s', country = '%(country)s', password = '%(password)s'  
                        WHERE handle = '%(old_handle)s';

                   """

sql_delete_user = """
                        DELETE FROM users
                               WHERE handle = '%(handle)s';
                  """

sql_top_x_rated_users = """
                        SELECT *
                        FROM top_users
                        LIMIT %(num)d;;
                    """


sql_top_x_contributors_users = """
                        SELECT users.handle, users.contribution
                        FROM users
                        ORDER BY users.contribution DESC, users.rating DESC
                        LIMIT %(num)d;
                    """

sql_countries = """
                         SELECT DISTINCT users.country
                         FROM users
                         ORDER BY users.country;
                    """

sql_users = """
                SELECT users.handle, users.rating, users.contribution, COUNT(*) as numfollowers
                FROM users JOIN friends ON users.handle = friends.handle2 
                WHERE users.handle LIKE '%(handle)s' AND users.rating %(rop)s %(rating)d AND users.contribution %(cntrop)s %(contribution)d AND users.country LIKE '%(country)s'
                GROUP BY users.handle
                HAVING COUNT(*) %(fcmp)s %(numfollowers)s
                ORDER BY users.rating DESC
                LIMIT %(length)d OFFSET %(offset)d;

            """

sql_num_followers = """
                SELECT COUNT(*)
                FROM friends
                WHERE friends.handle2 = '%(handle1)s';
            """

sql_check_follower = """
                SELECT friends.handle1, friends.handle2
                FROM friends
                WHERE friends.handle1 = '%(handle1)s' AND friends.handle2 = '%(handle2)s';
            """

sql_make_follower = """
                INSERT INTO friends VALUES ('%(handle1)s', '%(handle2)s');
            """


sql_make_unfollower = """
                DELETE FROM friends 
                WHERE friends.handle1 = '%(handle1)s' AND friends.handle2 = '%(handle2)s';
            """

sql_get_tags = """
                SELECT ARRAY_AGG(DISTINCT ptags)
                FROM problems, UNNEST(problems.tags) AS ptags;
            """

sql_search_problems = """
                SELECT *
                FROM problems
                WHERE problems.rating %(rop)s %(rating)d AND ARRAY %(ptags)s <@ problems.tags
                LIMIT %(length)d OFFSET %(offset)d;
            """
sql_search_problems_without_tags = """
                SELECT *
                FROM problems
                WHERE problems.rating %(rop)s %(rating)d 
                LIMIT %(length)d OFFSET %(offset)d;
            """


sql_get_problem = """
                SELECT *
                FROM problems
                WHERE problems.problemIndex = '%(index)s' AND problems.contestId = %(contestId)d;
            """

sql_get_contest = """
                SELECT *
                FROM contests
                WHERE contests.contestId = %(contestId)d;
            """

sql_get_ongoing_contests = """
                SELECT *
                FROM contests
                WHERE contests.status = 'ONGOING';
            """

sql_get_upcoming_contests = """
                SELECT *
                FROM contests
                WHERE contests.status = 'UPCOMING';
            """

sql_get_finished_contests = """
                SELECT *
                FROM contests
                WHERE contests.status = 'FINISHED'
                ORDER BY contests.contestDate DESC
                LIMIT %(length)d OFFSET %(offset)d;
            """

sql_get_recent_contests = """
                SELECT DISTINCT rcontests.contestId , rcontests.contestName, rcontests.contestDate, rcontests.problems, rcontests.status, rcontests.duration
                FROM 
                (SELECT contests.contestId , contests.contestName, contests.contestDate, contests.problems, contests.status, contests.duration, submissions.submissionTime

                FROM submissions JOIN contests ON contests.contestId = submissions.contestId
                WHERE submissions.author = '%(handle)s'
                ORDER BY submissions.submissionTime
                LIMIT 30) AS rcontests;
            """

sql_get_contest = """
                SELECT *
                FROM contests
                WHERE contests.contestId = %(contestId)d;
            """

sql_get_contest_data = """
                SELECT *
                FROM problems
                WHERE problems.contestId = %(contestId)d
                ORDER BY problems.problemIndex;
            """


sql_get_max_contest_id = """
                SELECT MAX(contests.contestId)
                FROM contests;
            """

sql_create_contest = """
                INSERT INTO contests VALUES (%(contestId)d, '%(contestName)s', ARRAY %(problems)s, 'UPCOMING', %(duration)d, CAST( '%(contestDate)s' as timestamp )  );
            """

sql_create_problem = """
                INSERT INTO problems VALUES ('%(name)s', %(contest_id)d, '%(problemIndex)s', %(rating)d, ARRAY %(tags)s, %(points)d, '%(url)s'    );
            """

sql_make_contest_running = """
                UPDATE contests SET status = 'ONGOING' where contestId = %(contestId)d;
            """

sql_make_contest_finished = """
                UPDATE contests SET status = 'FINISHED' where contestId = %(contestId)d;
            """

sql_get_submissions = """
                SELECT * 
                FROM submissions
                WHERE submissions.contestId = %(contestId)d AND submissions.author = '%(handle)s';
            """

sql_add_submission  = """
                INSERT INTO submissions VALUES ( %(values)s );

            """
sql_blogs_list = """
                SELECT blogs.blogId, blogs.heading, blogs.handle, blogs.comments_count
                FROM blogs 
                INNER JOIN users
                ON blogs.handle = users.handle
                """
sql_blog_fetch = """
                SELECT *
                FROM blogs
                WHERE blogs.blogId = %(blogId)d;
                """

sql_top_blogs = """
                SELECT blogs.blogId, blogs.heading, blogs.handle, blogs.comments_count
                FROM blogs 
                INNER JOIN users
                ON blogs.handle = users.handle
                ORDER BY
                blogs.comments_count, blogs.blogId
                LIMIT 5;
                """

sql_contest_standing = """
                        SELECT *
                        FROM contest_submissions
                        WHERE contest_submissions.contestId = %(contestId)d
                        ORDER BY contest_submissions.standing;
                        """
sql_contest_info_individual = """
                SELECT *
                FROM contests
                WHERE contests.contestId = %(contestId)d;
            """

sql_contest_data_individual = """
                SELECT *
                FROM problems
                WHERE problems.contestId = %(contestId)d;
            """

sql_update_contributions = """
                UPDATE users
                SET contribution = %(contribution)d
                WHERE users.handle = '%(handle)s';
            """

sql_update_blog_reports = """
                UPDATE blogs
                SET comments_count = %(report_count)d
                WHERE blogs.blogId = '%(blogId)d';
            """



# Views
sql_create_view_top_x_rated_users = """
                                CREATE MATERIALIZED VIEW top_users(handle, rating) AS
                                SELECT users.handle, users.rating
                                FROM users
                                ORDER BY users.rating DESC
                                LIMIT 1000;
                                """


# Triggers


sql_report_trigger = """
                        CREATE OR REPLACE FUNCTION
                        del_blog_on_report() RETURNS TRIGGER AS
                        $BODY$
                        BEGIN
                            DELETE FROM blogs
                            WHERE comments_count >= 5 ;
                            RETURN old;
                        END;
                        $BODY$ 
                        language plpgsql;
                    """


sql_create_report_trigger = """
                            CREATE TRIGGER  delBlogOnReport
                            AFTER UPDATE ON blogs
                            FOR EACH ROW
                                EXECUTE PROCEDURE
                                    del_blog_on_report();
                            """

