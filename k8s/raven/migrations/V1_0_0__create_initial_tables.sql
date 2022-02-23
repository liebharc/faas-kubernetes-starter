CREATE TABLE Journal (
    id uuid NOT NULL,
    version int NOT NULL,
    entries json NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE Contacts (
    id uuid NOT NULL,
    version int NOT NULL,
    entries json NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE Challenges (
    id uuid NOT NULL,
    version int NOT NULL,
    entries json NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE Goals (
    id uuid NOT NULL,
    version int NOT NULL,
    entries json NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE CheckIns (
    id uuid NOT NULL,
    version int NOT NULL,
    entries json NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE SessionProgress (
    id uuid NOT NULL,
    version int NOT NULL,
    entries json NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE ContactRequests (
    id uuid NOT NULL,
    version int NOT NULL,
    entries json NOT NULL,
    PRIMARY KEY (id)
);