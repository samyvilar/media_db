

CREATE DATABASE media;
CREATE TABLE images (filename               VARCHAR NULL,
                     title                  VARCHAR NULL,
                     description            TEXT NULL,
                     source                 blob,
                     edge_map               blob,
                     histogram              blob,
                     histogram_edege_map    blob);

CREATE TABLE videos (filename               VARCHAR NULL,
                     title                  VARCHAR NULL,
                     description            TEXT NULL,
                     source                 blob,
                     ...)
