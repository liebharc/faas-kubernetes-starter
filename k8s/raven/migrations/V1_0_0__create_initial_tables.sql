CREATE TABLE HelloWorld (
    id uuid NOT NULL,
    version int NOT NULL,
    document json NOT NULL,
    PRIMARY KEY (id)
);