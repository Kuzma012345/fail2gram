SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

INSERT INTO public.users (id, login, password_digest, user_role) OVERRIDING SYSTEM VALUE VALUES (1, 'host_rainbow', '$argon2id$v=19$m=65536,t=4,p=2$cLYJGlmBYqa75eEnsYtMFA$pXRSoCRZR0P7EUsqTluDMg4diOPbjSmTlXmOITQYsrQ', 'admin');
INSERT INTO public.users (id, login, password_digest, user_role) OVERRIDING SYSTEM VALUE VALUES (2, 'nee_chan', '$argon2id$v=19$m=65536,t=4,p=2$0bhBxQkG5RwV/MUN3zzkNg$xlZiLZjA9oZUidpsEOCVvMWAHPMtYRYvG+QMtqYSOxs', 'admin');

SELECT pg_catalog.setval('public.users_id_seq', 2, true);
