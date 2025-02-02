CREATE EXTENSION IF NOT EXISTS dblink;
DO
$do$
BEGIN
   IF EXISTS (SELECT FROM pg_database WHERE datname = 'matomo_data') THEN
      RAISE NOTICE 'Database already exists';  -- optional
ELSE
      PERFORM dblink_exec('dbname=' || current_database()  -- current db
                        , 'CREATE DATABASE matomo_data');
END IF;
END
$do$;