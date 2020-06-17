create table domain_tasks (
    id           integer primary key autoincrement not null,
    name         text not null,
    run_status   text not null,
    domains      text not null,
    permitted    text not null,
    autofunc     text,
    directories  text,
    included     text
);

create table email_tasks (
    id           integer primary key autoincrement not null,
    name         text not null,
    run_status   text not null,
    emails       text not null,
    permitted    text not null,
    autofunc     text,
    directories  text,
    included     text
);

create table open_results (
    id           text primary key not null,
    file_name    text not null,
    trashed      text not null,
    emails       text not null,
    created_at   date text not null
);

create table certified_results (
    id           text primary key not null,
    file_name    text not null,
    trashed      text not null,
    emails       text not null,
    created_at   date text not null
);