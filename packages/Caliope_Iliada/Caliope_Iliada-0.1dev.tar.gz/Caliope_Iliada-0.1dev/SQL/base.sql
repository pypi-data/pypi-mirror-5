
-- Created on 27/05/2013
-- 
-- @author: Andrés Felipe Calderón andres.calderon@correlibre.org
-- @license:  GNU AFFERO GENERAL PUBLIC LICENSE
-- 
-- Caliope Storage is the base of Caliope's Framework
-- Copyright (C) 2013 Fundación Correlibre
-- 
--     This program is free software: you can redistribute it and/or modify
--     it under the terms of the GNU Affero General Public License as published by
--     the Free Software Foundation, either version 3 of the License, or
--     (at your option) any later version.
-- 
--     This program is distributed in the hope that it will be useful,
--     but WITHOUT ANY WARRANTY; without even the implied warranty of
--     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
--     GNU Affero General Public License for more details.
-- 
--     You should have received a copy of the GNU Affero General Public License
--     along with this program.  If not, see <http://www.gnu.org/licenses/>.

CREATE SEQUENCE serial_caliope START 1;

Create TABLE CALIOPE_NODE_TYPES(
    ID_NODE_TYPE serial NOT NULL, 
    NAME text NOT NULL, 
    PRIMARY KEY (ID_NODE_TYPE),
    UNIQUE (NAME)
    );
    
INSERT INTO CALIOPE_NODE_TYPES (NAME)
    VALUES ('connection_node');


Create TABLE CALIOPE_NODES(
    UUID_NODE  character(36) NOT NULL, 
    TS timestamp  NOT NULL default LOCALTIMESTAMP, 
    NODE_TYPE integer NOT NULL references CALIOPE_NODE_TYPES(ID_NODE_TYPE), 
    ID_ANCESTOR_NODE integer, 
    PRIMARY KEY (UUID_NODE)
    );

Create TABLE CALIOPE_ATTRIBUTE_TYPES(
    NAME text NOT NULL, 
    ID_ATTRIBUTE_TYPE  serial NOT NULL, 
    NODE_ATTRIBUTE_TABLE text NOT NULL,     
    PRIMARY KEY  (NAME),
    UNIQUE (ID_ATTRIBUTE_TYPE)
    );
    
INSERT INTO CALIOPE_ATTRIBUTE_TYPES (NAME, NODE_ATTRIBUTE_TABLE)
    VALUES ('integer',  'CALIOPE_ATTRIBUTE_INTEGER');

INSERT INTO CALIOPE_ATTRIBUTE_TYPES (NAME, NODE_ATTRIBUTE_TABLE)
    VALUES ('double',  'CALIOPE_ATTRIBUTE_DOUBLE');
    
INSERT INTO CALIOPE_ATTRIBUTE_TYPES (NAME, NODE_ATTRIBUTE_TABLE)
    VALUES ('blob',  'CALIOPE_ATTRIBUTE_BYTEA');

INSERT INTO CALIOPE_ATTRIBUTE_TYPES (NAME, NODE_ATTRIBUTE_TABLE)
    VALUES ('timestamp',  'CALIOPE_ATTRIBUTE_TIMESTAMP');
    
INSERT INTO CALIOPE_ATTRIBUTE_TYPES (NAME, NODE_ATTRIBUTE_TABLE)
    VALUES ('bool',  'CALIOPE_ATTRIBUTE_BOOLEAN');
    
INSERT INTO CALIOPE_ATTRIBUTE_TYPES (NAME, NODE_ATTRIBUTE_TABLE)
    VALUES ('text',  'CALIOPE_ATTRIBUTE_TEXT');
    
    
Create TABLE CALIOPE_ATTRIBUTES(
    ID_ATTRIBUTE bigserial NOT NULL, 
    UUID_NODE character(36) NOT NULL references CALIOPE_NODES(UUID_NODE), 
    KEY_NAME  text  NOT NULL, 
    PRIMARY KEY (ID_ATTRIBUTE),
    UNIQUE (UUID_NODE,KEY_NAME)
    );

Create TABLE CALIOPE_ATTRIBUTE_INTEGER(
    ID_ATTRIBUTE integer NOT NULL references CALIOPE_ATTRIBUTES(ID_ATTRIBUTE), 
    VALUE integer NOT NULL, 
    PRIMARY KEY (ID_ATTRIBUTE,VALUE)
    );
    
Create TABLE CALIOPE_ATTRIBUTE_VALUE_DOUBLE(
    ID_ATTRIBUTE integer NOT NULL references CALIOPE_ATTRIBUTES(ID_ATTRIBUTE), 
    VALUE double precision NOT NULL, 
    PRIMARY KEY (ID_ATTRIBUTE,VALUE)
    );
        
Create TABLE CALIOPE_ATTRIBUTE_VALUE_BYTEA(
    ID_ATTRIBUTE integer NOT NULL references CALIOPE_ATTRIBUTES(ID_ATTRIBUTE), 
    VALUE bytea  NOT NULL, 
    PRIMARY KEY (ID_ATTRIBUTE,VALUE)
    );
    
Create TABLE CALIOPE_ATTRIBUTE_VALUE_TIMESTAMP(
    ID_ATTRIBUTE integer NOT NULL references CALIOPE_ATTRIBUTES(ID_ATTRIBUTE), 
    VALUE timestamp NOT NULL, 
    PRIMARY KEY (ID_ATTRIBUTE,VALUE)
    );
    
Create TABLE CALIOPE_ATTRIBUTE_VALUE_BOOLEAN(
    ID_ATTRIBUTE integer NOT NULL references CALIOPE_ATTRIBUTES(ID_ATTRIBUTE), 
    VALUE boolean NOT NULL, 
    PRIMARY KEY (ID_ATTRIBUTE,VALUE)
    );
    
Create TABLE CALIOPE_ATTRIBUTE_VALUE_TEXT(
    ID_ATTRIBUTE integer NOT NULL references CALIOPE_ATTRIBUTES(ID_ATTRIBUTE), 
    VALUE text NOT NULL, 
    PRIMARY KEY (ID_ATTRIBUTE,VALUE)
    );
    
Create TABLE CALIOPE_EDGES(
    UUID_NODE_FROM character(36) NOT NULL references CALIOPE_NODES(UUID_NODE), 
    UUID_NODE_TO character(36)  NOT NULL references CALIOPE_NODES(UUID_NODE), 
    UUID_NODE_CONNECTOR character(36)  NOT NULL references CALIOPE_NODES(UUID_NODE), 
    PRIMARY KEY  (UUID_NODE_FROM, UUID_NODE_TO, UUID_NODE_CONNECTOR)
    );
 