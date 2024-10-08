/* SCHEMA */

drop table if exists domain_flag;
drop table if exists domain;
drop type if exists flags;
drop extension if exists btree_gist;

create type flags as enum ('EXPIRED', 'OUTZONE', 'DELETE_CANDIDATE');
create extension btree_gist;

create table domain (
	id serial primary key,
	domain_name varchar(255) not null, -- domain name max length is 255
	check (domain_name ~ '^[a-z0-9\.\-]*$'),
	registration_range tsrange not null,
	exclude using gist (
		registration_range with &&,
		domain_name with =
	),
	check (lower(registration_range) <> '-infinity')
);

create table domain_flag (
	id serial primary key,
	domain_id integer not null references domain(id) on delete cascade,
	flag_name flags not null,
	time_range tsrange not null,
	exclude using gist(
		time_range with &&,
		domain_id with =,
		flag_name with =
	),
	check (lower(time_range) <> '-infinity')
);

/*
Design choices:
The domain table deviates heavily from the task description. The domain_name is not 
unique, rather each registration is a new record. This models the real world scenario 
where a domain can be registered multiple times by different entities. 

The registration_range is a tsrange that defines the time when the domain is 
registered and unregistered. This type makes it very easy to not overlap domain records.

There is a slight problem when associating the domain_flag rows with the domain rows.
The foreign key should be the domain name, yet the domain name is not unique. This
problem might be solved by third table, domain_name, where only domain names are stored,
and is refferenced by the original domain table and the domain_flag table.
*/

/*
Proposals for additional constraints and enhancements:
1. Add a better regex name check for domain_name.
2. Add an indexes to improve query performance.
*/

/* SEED (TEST) DATA */
insert into public.domain(id, domain_name, registration_range)
values 
    (1001, 'www.domena.cz','[2000-01-01 14:30, 2000-12-31 15:30)')
,   (1002, 'www.domena.cz','[2001-01-01 14:30, 2001-12-31 15:30)')
,   (1003, 'www.domena.cz','[2002-01-01 14:30, 2002-12-31 15:30)')
,   (1004, 'www.domena.cz','[2003-01-01 14:30, 2003-12-31 15:30)')
,   (1005, 'www.domena.cz','[2004-01-01 14:30, 2004-12-31 15:30)')
,   (1006, 'www.neexpirovana.cz','[2000-01-01 14:30, 2025-12-31 15:30]')
,   (1007, 'www.expirovana.cz','[2000-01-01 14:30, 2025-12-31 15:30]')
,   (1008, 'www.expirovana-v-minulosti.cz','[2000-01-01 14:30, 2025-12-31 15:30]')
,   (1009, 'www.outzoned-v-minulosti.cz','[2000-01-01 14:30, 2025-12-31 15:30]')
,   (1010, 'www.expirovana-i-outzonovana-v-minulosti.cz','[2000-01-01 14:30, 2025-12-31 15:30]');

insert into public.domain_flag(domain_id, flag_name, time_range)
values
    (1001,'DELETE_CANDIDATE','[2000-12-31 15:30, 2000-12-31 15:31]')
,   (1002,'DELETE_CANDIDATE','[2001-12-31 15:30, 2001-12-31 15:31]')
,   (1003,'DELETE_CANDIDATE','[2002-12-31 15:30, 2002-12-31 15:31]')
,   (1004,'DELETE_CANDIDATE','[2003-12-31 15:30, 2003-12-31 15:31]')
,   (1005,'DELETE_CANDIDATE','[2004-12-31 15:30, 2004-12-31 15:31]')
,   (1007,'EXPIRED','[2024-01-01 15:30, 2025-12-31 15:30]')
,   (1008,'EXPIRED','[2023-01-01 15:30, 2023-12-31 15:30]')
,   (1009,'OUTZONE','[2023-01-01 15:30, 2023-12-31 15:30]')
,   (1010,'EXPIRED','[2023-01-01 15:30, 2023-12-31 15:30]')
,   (1010,'OUTZONE','[2023-01-01 15:30, 2023-12-31 15:30]');


/* QUERIES */

select d.domain_name
from public.domain d
where upper(d.registration_range) > now()
and lower(d.registration_range) < now()
and d.domain_name not in (
	select dd.domain_name
	from public.domain_flag df
    join public.domain dd on df.domain_id = dd.id
	where df.flag_name = 'EXPIRED'
	and upper(df.time_range) > now()
	and lower(df.time_range) < now()
);

select dd.domain_name
from public.domain_flag df
join public.domain dd on df.domain_id = dd.id
where df.flag_name = 'EXPIRED'
and dd.domain_name in (
	select dd2.domain_name
	from public.domain_flag df2
	join public.domain dd2 on df2.domain_id = dd2.id
	where df2.flag_name = 'OUTZONE'
	and upper(df2.time_range) < now()
)
and upper(df.time_range) < now();
