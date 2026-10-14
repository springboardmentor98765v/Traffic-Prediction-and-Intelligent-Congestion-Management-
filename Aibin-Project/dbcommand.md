============================================================
POSTGRESQL COMMANDS - TRAFFICVISION AI
============================================================

# 1. Check PostgreSQL version
SELECT version();


# 2. Show current database
SELECT current_database();


# 3. Show current PostgreSQL user
SELECT current_user;


# 4. List ALL databases
\l


# 5. Connect to a specific database
\c database_name

# Example:
\c postgres


# 6. Show the current database
SELECT current_database();


============================================================
TABLES
============================================================

# 7. Show all tables in the current database
\dt


# 8. Show all tables in the public schema
\dt public.*


# 9. Show tables from ALL schemas
\dt *.*


# 10. Show only table names
SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;


# 11. Check if a specific table exists
\dt users


============================================================
TABLE STRUCTURE / SCHEMA
============================================================

# 12. Show structure of a table
\d users


# 13. Show detailed structure of a table
\d+ users


# 14. Show structure of roles
\d roles


# 15. Show structure of user_sessions
\d user_sessions


# 16. Show structure of roads
\d roads


# 17. Show structure of sensors
\d sensors


# 18. Show structure of all public tables
\d


============================================================
VIEW DATA INSIDE TABLES
============================================================

# 19. Show all users
SELECT * FROM users;


# 20. Show all roles
SELECT * FROM roles;


# 21. Show all user sessions / refresh tokens
SELECT * FROM user_sessions;
SELECT * FROM refresh_tokens;


# 22. Show all roads
SELECT * FROM roads;


# 23. Show all sensors
SELECT * FROM sensors;


# 24. Show all traffic readings
SELECT * FROM traffic_readings;


# 25. Show all congestion history
SELECT * FROM congestion_history;


# 26. Show all road capacity records
SELECT * FROM road_capacity;


# 27. Show all traffic staging records
SELECT * FROM traffic_staging;


============================================================
COUNT RECORDS
============================================================

# 28. Count users
SELECT COUNT(*) FROM users;


# 29. Count roles
SELECT COUNT(*) FROM roles;


# 30. Count roads
SELECT COUNT(*) FROM roads;


# 31. Count sensors
SELECT COUNT(*) FROM sensors;


# 32. Count traffic readings
SELECT COUNT(*) FROM traffic_readings;


# 33. Count congestion history
SELECT COUNT(*) FROM congestion_history;


============================================================
USEFUL DATABASE INFORMATION
============================================================

# 34. Show all schemas
\dn


# 35. Show database size
SELECT pg_size_pretty(
    pg_database_size(current_database())
);


# 36. Show all databases with their sizes
SELECT
    datname,
    pg_size_pretty(pg_database_size(datname))
FROM pg_database
ORDER BY datname;


# 37. Show PostgreSQL server connection information
\conninfo


============================================================
USERS / ROLES
============================================================

# 38. Show PostgreSQL users/roles
\du


# 39. Show current PostgreSQL user
SELECT current_user;


# 40. Show application roles stored in TrafficVision
SELECT * FROM roles;


# 41. Show application users
SELECT
    id,
    name,
    email,
    role,
    created_at
FROM users;


============================================================
CHECK TABLE RELATIONSHIPS
============================================================

# 42. Show detailed users table including foreign keys
\d+ users


# 43. Show detailed user_sessions table including foreign keys
\d+ user_sessions


# 44. Show detailed roles table
\d+ roles


============================================================
SEARCH / FILTER DATA
============================================================

# 45. Find a user by email
SELECT *
FROM users
WHERE email = 'admin@trafficvision.ai';


# 46. Find users with Admin role
SELECT *
FROM users
WHERE role = 'admin' OR role = 'Admin';


# 47. Find traffic operators
SELECT *
FROM users
WHERE role = 'traffic_operator' OR role = 'Operator';


# 48. Find public commuters
SELECT *
FROM users
WHERE role = 'public' OR role = 'Public';


============================================================
ORDER DATA
============================================================

# 49. Show newest users first
SELECT *
FROM users
ORDER BY created_at DESC;


# 50. Show oldest users first
SELECT *
FROM users
ORDER BY created_at ASC;


============================================================
IMPORTANT PSQL COMMANDS
============================================================

# 51. Quit PostgreSQL
\q


# 52. Clear the terminal screen
Ctrl + L


# 53. Show help for psql commands
\?


# 54. Show help for SQL commands
\h


# 55. Get help for SELECT
\h SELECT


============================================================
RUN SQL FILE
============================================================

# 56. Execute a SQL file from inside psql

\i 'C:/path/to/schema.sql'


# Example:
\i 'C:/Users/AIBIN SHIBU/OneDrive/Documents/trafficvision/aibin-backend/database/schema.sql'


============================================================
TRAFFICVISION - QUICK CHECK
============================================================

# Check all tables
\dt public.*

# Check users table
\d users

# Check roles table
\d roles

# Check sessions table
\d user_sessions

# See users
SELECT * FROM users;

# See roles
SELECT * FROM roles;

# See sessions
SELECT * FROM user_sessions;

# See all public tables
\dt public.*

============================================================
END
============================================================
