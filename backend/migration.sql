BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> c7bb4adc4f67

CREATE TABLE users (
    id SERIAL NOT NULL,
    email VARCHAR,
    hashed_password VARCHAR,
    is_active BOOLEAN,
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE INDEX ix_users_id ON users (id);

CREATE TABLE debates (
    id SERIAL NOT NULL,
    topic VARCHAR,
    created_at TIMESTAMP WITHOUT TIME ZONE,
    client_1_id INTEGER,
    client_2_id INTEGER,
    PRIMARY KEY (id),
    FOREIGN KEY(client_1_id) REFERENCES users (id),
    FOREIGN KEY(client_2_id) REFERENCES users (id)
);

CREATE INDEX ix_debates_id ON debates (id);

CREATE INDEX ix_debates_topic ON debates (topic);

CREATE TABLE messages (
    id SERIAL NOT NULL,
    debate_id INTEGER,
    sender_id INTEGER,
    content TEXT,
    timestamp TIMESTAMP WITHOUT TIME ZONE,
    PRIMARY KEY (id),
    FOREIGN KEY(debate_id) REFERENCES debates (id),
    FOREIGN KEY(sender_id) REFERENCES users (id)
);

CREATE INDEX ix_messages_id ON messages (id);

INSERT INTO alembic_version (version_num) VALUES ('c7bb4adc4f67') RETURNING alembic_version.version_num;

-- Running upgrade c7bb4adc4f67 -> bc4d17171708

ALTER TABLE debates ADD COLUMN user_id INTEGER NOT NULL;

ALTER TABLE debates ADD COLUMN stance VARCHAR NOT NULL;

ALTER TABLE debates ALTER COLUMN topic SET NOT NULL;

DROP INDEX ix_debates_topic;

ALTER TABLE debates DROP CONSTRAINT debates_client_1_id_fkey;

ALTER TABLE debates DROP CONSTRAINT debates_client_2_id_fkey;

ALTER TABLE debates ADD FOREIGN KEY(user_id) REFERENCES users (id);

ALTER TABLE debates DROP COLUMN client_2_id;

ALTER TABLE debates DROP COLUMN client_1_id;

ALTER TABLE debates DROP COLUMN created_at;

ALTER TABLE messages ALTER COLUMN debate_id SET NOT NULL;

ALTER TABLE messages ALTER COLUMN sender_id SET NOT NULL;

ALTER TABLE messages ALTER COLUMN content SET NOT NULL;

ALTER TABLE users ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT now();

ALTER TABLE users ALTER COLUMN email SET NOT NULL;

ALTER TABLE users ALTER COLUMN hashed_password SET NOT NULL;

ALTER TABLE users DROP COLUMN is_active;

UPDATE alembic_version SET version_num='bc4d17171708' WHERE alembic_version.version_num = 'c7bb4adc4f67';

-- Running upgrade bc4d17171708 -> 8d5b7cd962a2

ALTER TABLE users ADD COLUMN username VARCHAR NOT NULL;

CREATE UNIQUE INDEX ix_users_username ON users (username);

UPDATE alembic_version SET version_num='8d5b7cd962a2' WHERE alembic_version.version_num = 'bc4d17171708';

-- Running upgrade 8d5b7cd962a2 -> cf8215e87da5

ALTER TABLE users ADD COLUMN elo INTEGER;

ALTER TABLE users ADD COLUMN mind_tokens INTEGER;

UPDATE alembic_version SET version_num='cf8215e87da5' WHERE alembic_version.version_num = '8d5b7cd962a2';

-- Running upgrade cf8215e87da5 -> a63c2c2d4b2d

ALTER TABLE debates ADD COLUMN winner VARCHAR;

ALTER TABLE debates ADD COLUMN timestamp TIMESTAMP WITHOUT TIME ZONE;

UPDATE alembic_version SET version_num='a63c2c2d4b2d' WHERE alembic_version.version_num = 'cf8215e87da5';

-- Running upgrade a63c2c2d4b2d -> b8c3e3e7e7a7

CREATE TABLE badges (
    id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    description VARCHAR NOT NULL,
    PRIMARY KEY (id)
);

CREATE INDEX ix_badges_id ON badges (id);

CREATE UNIQUE INDEX ix_badges_name ON badges (name);

CREATE TABLE streaks (
    id SERIAL NOT NULL,
    user_id INTEGER NOT NULL,
    current_streak INTEGER,
    max_streak INTEGER,
    PRIMARY KEY (id),
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_streaks_id ON streaks (id);

CREATE TABLE user_badges (
    id SERIAL NOT NULL,
    user_id INTEGER NOT NULL,
    badge_id INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(badge_id) REFERENCES badges (id),
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_user_badges_id ON user_badges (id);

UPDATE alembic_version SET version_num='b8c3e3e7e7a7' WHERE alembic_version.version_num = 'a63c2c2d4b2d';

-- Running upgrade b8c3e3e7e7a7 -> d48a8d5f6b9a

CREATE TABLE forums (
    id SERIAL NOT NULL,
    name VARCHAR NOT NULL,
    description VARCHAR NOT NULL,
    PRIMARY KEY (id)
);

CREATE INDEX ix_forums_id ON forums (id);

CREATE UNIQUE INDEX ix_forums_name ON forums (name);

CREATE TABLE threads (
    id SERIAL NOT NULL,
    title VARCHAR NOT NULL,
    forum_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(forum_id) REFERENCES forums (id),
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_threads_id ON threads (id);

CREATE INDEX ix_threads_title ON threads (title);

CREATE TABLE posts (
    id SERIAL NOT NULL,
    content TEXT NOT NULL,
    thread_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY(thread_id) REFERENCES threads (id),
    FOREIGN KEY(user_id) REFERENCES users (id)
);

CREATE INDEX ix_posts_id ON posts (id);

UPDATE alembic_version SET version_num='d48a8d5f6b9a' WHERE alembic_version.version_num = 'b8c3e3e7e7a7';

COMMIT;
