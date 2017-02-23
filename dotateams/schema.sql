drop table if exists team;
drop table if exists user;

create table user (
	id integer primary key autoincrement,
	username text not null,
	password text not null,
	constraint unique_uname unique(username)
);

create table team (
	id integer primary key autoincrement,
	user integer not null,
	title text not null,
	hero1 text,
	hero2 text,
	hero3 text,
	hero4 text,
	hero5 text,
	hero6 text,
	description text not null,
	alt1 text,
	alt2 text,
	alt3 text,
	other_alts text,
	counter1 text,
	counter2 text,
	counter3 text,
	other_counters text,
	foreign key(user) references user(id)
);