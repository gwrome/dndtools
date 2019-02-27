DROP TABLE IF EXISTS spell;

CREATE TABLE spell (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    spell_level INTEGER NOT NULL,
    school TEXT NOT NULL,
    source TEXT,
    cast_time TEXT NOT NULL,
    range TEXT NOT NULL,
    components TEXT,
    duration TEXT NOT NULL,
    ritual BIT NOT NULL DEFAULT 0,
    description TEXT NOT NULL
);