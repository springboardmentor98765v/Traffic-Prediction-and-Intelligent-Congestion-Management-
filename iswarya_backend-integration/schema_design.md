Table: USERS
----------------
id (Primary Key)
name (String)
email (String, Unique)
password_hash (String)
role (String) - Options: ADMIN, TRAFFIC_OPERATOR, PUBLIC
created_at (Timestamp)