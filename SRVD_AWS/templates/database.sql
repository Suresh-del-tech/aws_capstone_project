CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT, email TEXT, password TEXT);
CREATE TABLE trains(id INTEGER PRIMARY KEY, name TEXT, source TEXT, destination TEXT, time TEXT);
INSERT INTO trains(name,source,destination,time) VALUES
('Express 101','Chennai','Bangalore','06:00 AM'),
('Superfast 202','Delhi','Mumbai','09:30 PM');
