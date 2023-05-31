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

CREATE EXTENSION IF NOT EXISTS plpython3u WITH SCHEMA pg_catalog;

COMMENT ON EXTENSION plpython3u IS 'PL/Python3U untrusted procedural language';

CREATE TYPE public.event_kind AS ENUM (
    'track_added',
    'ban_added',
    'ban_removed'
);

ALTER TYPE public.event_kind OWNER TO postgres;

CREATE TYPE public.host_user_role AS ENUM (
    'viewer',
    'editor',
    'admin'
);

ALTER TYPE public.host_user_role OWNER TO postgres;

CREATE TYPE public.service_user_role AS ENUM (
    'viewer',
    'editor'
);

ALTER TYPE public.service_user_role OWNER TO postgres;

CREATE TYPE public.user_role AS ENUM (
    'viewer',
    'editor',
    'admin'
);

ALTER TYPE public.user_role OWNER TO postgres;

CREATE FUNCTION public.add_ban_event() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
begin
    insert into events (track_id, occurrence_time, kind) VALUES (new.track_id, now(), 'ban_added');
    return new;
end;
$$;

ALTER FUNCTION public.add_ban_event() OWNER TO postgres;

CREATE FUNCTION public.add_track_event() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
begin
    insert into events (track_id, occurrence_time, kind) VALUES (new.id, now(), 'track_added');
    return new;
end;
$$;

ALTER FUNCTION public.add_track_event() OWNER TO postgres;

CREATE FUNCTION public.remove_ban_event() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
begin
    insert into events (track_id, occurrence_time, kind) VALUES (new.track_id, now(), 'ban_removed');
    return new;
end;
$$;

ALTER FUNCTION public.remove_ban_event() OWNER TO postgres;

CREATE PROCEDURE public.unban_track(IN user_id integer, IN track_id integer)
    LANGUAGE plpython3u
    AS $_$
    privilege_query = plpy.prepare("""
select sar.user_role as user_role, b.id as ban_id
from users u
         join service_access_rules sar on u.id = sar.user_id
         join services s on s.id = sar.service_id
         join tracks t on s.id = t.service_id
         left join bans b on t.id = b.track_id
where u.id = $1
  and t.id = $2;
 """, ["integer", "integer"])

    privilege_row = privilege_query.execute([user_id, track_id], 1)

    if len(privilege_row) == 0:
        raise ValueError("No privilege found for the combination of user and track")

    user_role = privilege_row[0]["user_role"]

    if user_role not in ["editor"]:
        raise ValueError("User's privileges are not sufficient")

    ban_id = privilege_row[0]["ban_id"]

    if ban_id is None:
        raise ValueError("No ban found for the track")

    unban_query = plpy.prepare("""
delete from bans where id = $1;
    """, ["integer"])

    unban_query.execute([ban_id])
$_$;

ALTER PROCEDURE public.unban_track(IN user_id integer, IN track_id integer) OWNER TO postgres;

CREATE FUNCTION public.xor(a boolean, b boolean) RETURNS boolean
    LANGUAGE sql IMMUTABLE
    AS $$
    SELECT (a AND NOT b) OR (b AND NOT a);
    $$;

ALTER FUNCTION public.xor(a boolean, b boolean) OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

CREATE TABLE public.bans (
    id integer NOT NULL,
    track_id integer NOT NULL,
    begin_time timestamp without time zone NOT NULL,
    duration interval NOT NULL
);

ALTER TABLE public.bans OWNER TO postgres;

ALTER TABLE public.bans ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.bans_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE public.tracked_remotes (
    id integer NOT NULL,
    ip inet NOT NULL,
    first_observation_time timestamp without time zone NOT NULL,
    last_observation_time timestamp without time zone NOT NULL
);

ALTER TABLE public.tracked_remotes OWNER TO postgres;

CREATE TABLE public.tracks (
    id integer NOT NULL,
    service_id integer NOT NULL,
    tracked_remote_id integer NOT NULL,
    first_observation_time timestamp without time zone NOT NULL,
    last_observation_time timestamp without time zone NOT NULL,
    observations_count integer DEFAULT 0 NOT NULL
);

ALTER TABLE public.tracks OWNER TO postgres;

CREATE VIEW public.bans_view AS
 SELECT b.id AS ban_id,
    b.begin_time AS ban_begin_time,
    b.duration AS ban_duration,
    t.id AS track_id,
    tr.id AS tracked_remote_id,
    tr.ip AS tracked_remote_ip
   FROM ((public.bans b
     JOIN public.tracks t ON ((t.id = b.track_id)))
     JOIN public.tracked_remotes tr ON ((tr.id = t.tracked_remote_id)))
  ORDER BY b.begin_time;

ALTER TABLE public.bans_view OWNER TO postgres;

CREATE TABLE public.services (
    id integer NOT NULL,
    short_name character varying(32) NOT NULL,
    name character varying,
    host_id integer NOT NULL
);

ALTER TABLE public.services OWNER TO postgres;

CREATE VIEW public.connections_view AS
 SELECT s.id AS service_id,
    s.short_name AS service_short_name,
    s.name AS service_name,
    t.id AS track_id,
    t.first_observation_time,
    t.last_observation_time,
    tr.id AS tracked_remote_id,
    tr.ip AS tracked_remote_ip
   FROM ((public.tracks t
     JOIN public.services s ON ((s.id = t.service_id)))
     JOIN public.tracked_remotes tr ON ((tr.id = t.tracked_remote_id)))
  ORDER BY t.last_observation_time DESC;

ALTER TABLE public.connections_view OWNER TO postgres;

CREATE TABLE public.events (
    id integer NOT NULL,
    track_id integer NOT NULL,
    occurrence_time timestamp without time zone NOT NULL,
    kind public.event_kind NOT NULL
);

ALTER TABLE public.events OWNER TO postgres;

CREATE VIEW public.event_statistics_view AS
 SELECT count(events.kind) AS count,
    events.kind
   FROM public.events
  GROUP BY events.kind;

ALTER TABLE public.event_statistics_view OWNER TO postgres;

ALTER TABLE public.events ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.events_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE VIEW public.events_view AS
 SELECT e.id AS event_id,
    e.occurrence_time AS event_occurrence_time,
    e.kind AS event_kind,
    t.id AS track_id,
    tr.id AS tracked_remote_id,
    tr.ip AS tracked_remote_ip
   FROM ((public.events e
     JOIN public.tracks t ON ((e.track_id = t.id)))
     JOIN public.tracked_remotes tr ON ((tr.id = t.tracked_remote_id)))
  ORDER BY e.occurrence_time;

ALTER TABLE public.events_view OWNER TO postgres;

CREATE TABLE public.host_access_rules (
    id integer NOT NULL,
    host_id integer NOT NULL,
    user_id integer NOT NULL,
    user_role public.host_user_role NOT NULL
);

ALTER TABLE public.host_access_rules OWNER TO postgres;

ALTER TABLE public.host_access_rules ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.host_access_controls_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE public.hosts (
    id integer NOT NULL,
    hostname character varying(256),
    ip inet,
    CONSTRAINT hostname_ip_xor_check CHECK (public.xor((hostname IS NOT NULL), (ip IS NOT NULL))),
    CONSTRAINT hostname_lower_check CHECK (((hostname)::text = lower((hostname)::text)))
);

ALTER TABLE public.hosts OWNER TO postgres;

ALTER TABLE public.hosts ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.hosts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE public.service_access_rules (
    id integer NOT NULL,
    service_id integer NOT NULL,
    user_id integer NOT NULL,
    user_role public.service_user_role NOT NULL
);

ALTER TABLE public.service_access_rules OWNER TO postgres;

ALTER TABLE public.service_access_rules ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.service_access_controls_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

ALTER TABLE public.services ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.services_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE public.telegram_users (
    id integer NOT NULL,
    telegram_id bigint NOT NULL,
    user_id integer,
    pending_login_user_id integer,
    CONSTRAINT login_state_check CHECK ((NOT ((user_id IS NOT NULL) AND (pending_login_user_id IS NOT NULL))))
);

ALTER TABLE public.telegram_users OWNER TO postgres;

ALTER TABLE public.telegram_users ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.telegram_users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

ALTER TABLE public.tracked_remotes ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tracked_remotes_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

ALTER TABLE public.tracks ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tracks_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE public.users (
    id integer NOT NULL,
    login character varying(32) NOT NULL,
    password_digest character varying(128) NOT NULL,
    user_role public.user_role
);

ALTER TABLE public.users OWNER TO postgres;

ALTER TABLE public.users ALTER COLUMN id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

ALTER TABLE ONLY public.bans
    ADD CONSTRAINT bans_pk PRIMARY KEY (id);

ALTER TABLE ONLY public.bans
    ADD CONSTRAINT bans_pk2 UNIQUE (track_id);

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pk PRIMARY KEY (id);

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pk2 UNIQUE (track_id, kind);

ALTER TABLE ONLY public.host_access_rules
    ADD CONSTRAINT host_access_rules_pk PRIMARY KEY (id);

ALTER TABLE ONLY public.host_access_rules
    ADD CONSTRAINT host_access_rules_pk2 UNIQUE (host_id, user_id, user_role);

ALTER TABLE ONLY public.hosts
    ADD CONSTRAINT hosts_pk PRIMARY KEY (id);

ALTER TABLE ONLY public.hosts
    ADD CONSTRAINT hosts_pk2 UNIQUE (hostname);

ALTER TABLE ONLY public.hosts
    ADD CONSTRAINT hosts_pk3 UNIQUE (ip);

ALTER TABLE ONLY public.service_access_rules
    ADD CONSTRAINT service_access_rules_pk PRIMARY KEY (id);

ALTER TABLE ONLY public.service_access_rules
    ADD CONSTRAINT service_access_rules_pk2 UNIQUE (service_id, user_id, user_role);

ALTER TABLE ONLY public.services
    ADD CONSTRAINT services_pk PRIMARY KEY (id);

ALTER TABLE ONLY public.services
    ADD CONSTRAINT services_pk2 UNIQUE (short_name, host_id);

ALTER TABLE ONLY public.telegram_users
    ADD CONSTRAINT telegram_users_pk PRIMARY KEY (id);

ALTER TABLE ONLY public.telegram_users
    ADD CONSTRAINT telegram_users_pk2 UNIQUE (telegram_id);

ALTER TABLE ONLY public.telegram_users
    ADD CONSTRAINT telegram_users_pk3 UNIQUE (user_id);

ALTER TABLE ONLY public.tracked_remotes
    ADD CONSTRAINT tracked_remotes_pk PRIMARY KEY (id);

ALTER TABLE ONLY public.tracked_remotes
    ADD CONSTRAINT tracked_remotes_pk2 UNIQUE (ip);

ALTER TABLE ONLY public.tracks
    ADD CONSTRAINT tracks_pk PRIMARY KEY (id);

ALTER TABLE ONLY public.tracks
    ADD CONSTRAINT tracks_pk2 UNIQUE (service_id, tracked_remote_id);

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pk PRIMARY KEY (id);

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pk2 UNIQUE (login);

CREATE INDEX tracked_remotes_first_observation_time_index ON public.tracked_remotes USING btree (first_observation_time);

CREATE INDEX tracked_remotes_last_observation_time_index ON public.tracked_remotes USING btree (last_observation_time);

CREATE TRIGGER ban_added AFTER INSERT ON public.bans FOR EACH ROW EXECUTE FUNCTION public.add_ban_event();

CREATE TRIGGER ban_removed AFTER DELETE ON public.bans FOR EACH ROW EXECUTE FUNCTION public.remove_ban_event();

CREATE TRIGGER track_added AFTER INSERT ON public.tracks FOR EACH ROW EXECUTE FUNCTION public.add_track_event();

ALTER TABLE ONLY public.bans
    ADD CONSTRAINT bans_tracks_id_fk FOREIGN KEY (track_id) REFERENCES public.tracks(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_tracks_id_fk FOREIGN KEY (track_id) REFERENCES public.tracks(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.host_access_rules
    ADD CONSTRAINT host_access_rules_hosts_id_fk FOREIGN KEY (host_id) REFERENCES public.hosts(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.host_access_rules
    ADD CONSTRAINT host_access_rules_users_id_fk FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.service_access_rules
    ADD CONSTRAINT service_access_rules_services_id_fk FOREIGN KEY (service_id) REFERENCES public.services(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.service_access_rules
    ADD CONSTRAINT service_access_rules_users_id_fk FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.services
    ADD CONSTRAINT services_hosts_id_fk FOREIGN KEY (host_id) REFERENCES public.hosts(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.telegram_users
    ADD CONSTRAINT telegram_users_users_id_fk FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;

ALTER TABLE ONLY public.telegram_users
    ADD CONSTRAINT telegram_users_users_id_fk2 FOREIGN KEY (pending_login_user_id) REFERENCES public.users(id) ON DELETE SET NULL;

ALTER TABLE ONLY public.tracks
    ADD CONSTRAINT tracks_services_id_fk FOREIGN KEY (service_id) REFERENCES public.services(id) ON DELETE CASCADE;

ALTER TABLE ONLY public.tracks
    ADD CONSTRAINT tracks_tracked_remotes_id_fk FOREIGN KEY (tracked_remote_id) REFERENCES public.tracked_remotes(id) ON DELETE RESTRICT;

GRANT SELECT ON TABLE public.bans TO frontend;
GRANT SELECT,INSERT ON TABLE public.bans TO backend;
GRANT SELECT,INSERT,DELETE,TRUNCATE,UPDATE ON TABLE public.bans TO admin;

GRANT SELECT ON TABLE public.tracked_remotes TO frontend;
GRANT SELECT,INSERT ON TABLE public.tracked_remotes TO backend;
GRANT SELECT,INSERT,DELETE,TRUNCATE,UPDATE ON TABLE public.tracked_remotes TO admin;

GRANT SELECT ON TABLE public.tracks TO frontend;
GRANT SELECT,INSERT ON TABLE public.tracks TO backend;
GRANT SELECT,INSERT,DELETE,TRUNCATE,UPDATE ON TABLE public.tracks TO admin;

GRANT SELECT ON TABLE public.bans_view TO frontend;

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.services TO frontend;
GRANT SELECT ON TABLE public.services TO backend;
GRANT SELECT,INSERT,DELETE,TRUNCATE,UPDATE ON TABLE public.services TO admin;

GRANT SELECT ON TABLE public.connections_view TO frontend;

GRANT SELECT ON TABLE public.events TO frontend;
GRANT SELECT ON TABLE public.events TO backend;
GRANT SELECT,INSERT,DELETE,TRUNCATE,UPDATE ON TABLE public.events TO admin;

GRANT SELECT ON TABLE public.events_view TO frontend;

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.host_access_rules TO frontend;
GRANT SELECT,INSERT,DELETE,TRUNCATE,UPDATE ON TABLE public.host_access_rules TO admin;

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.hosts TO frontend;
GRANT SELECT ON TABLE public.hosts TO backend;
GRANT SELECT,INSERT,DELETE,TRUNCATE,UPDATE ON TABLE public.hosts TO admin;

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.service_access_rules TO frontend;
GRANT SELECT,INSERT,DELETE,TRUNCATE,UPDATE ON TABLE public.service_access_rules TO admin;

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE public.telegram_users TO frontend;
GRANT SELECT,INSERT,DELETE,TRUNCATE,UPDATE ON TABLE public.telegram_users TO admin;

GRANT SELECT,UPDATE ON TABLE public.users TO frontend;
GRANT SELECT,INSERT,DELETE,TRUNCATE,UPDATE ON TABLE public.users TO admin;
