
CREATE TABLE query1 AS
SELECT g_vs.name, COUNT(h_sr.movieid) AS moviecount
FROM genres AS g_vs, hasagenre AS h_sr
WHERE g_vs.genreid = h_sr.genreid
GROUP BY g_vs.genreid;

CREATE TABLE query2 AS
SELECT g_ab.name, AVG(r_rb.rating) AS rating
FROM genres AS g_ab, ratings AS r_rb, hasagenre AS h_ar
WHERE g_ab.genreid = h_ar.genreid AND h_ar.movieid = r_rb.movieid
GROUP BY g_ab.name;

CREATE TABLE query3 AS
SELECT m_rr.title, COUNT(r_rs.rating) AS countofratings
FROM movies AS m_rr, ratings AS r_rs
WHERE m_rr.movieid = r_rs.movieid
GROUP BY m_rr.title
HAVING COUNT(r_rs.rating) >= 10;

CREATE TABLE query4 AS
SELECT m_pv.movieid, m_pv.title
FROM movies AS m_pv, hasagenre AS h_vv, genres AS g_jv
WHERE h_vv.genreid = g_jv.genreid AND m_pv.movieid = h_vv.movieid
GROUP BY m_pv.movieid, g_jv.name
HAVING g_jv.name = 'Comedy';

CREATE TABLE query5 AS
SELECT m_jv.title, AVG(r_vc.rating) AS average
FROM movies AS m_jv, ratings AS r_vc
WHERE m_jv.movieid = r_vc.movieid
GROUP BY m_jv.title;

CREATE TABLE query6 AS
SELECT AVG(r_cp.rating) AS average
FROM movies AS m_pc, ratings AS r_cp, hasagenre AS h_pp, genres AS g_c
WHERE h_pp.genreid = g_c.genreid AND m_pc.movieid = r_cp.movieid AND h_pp.movieid = m_pc.movieid
GROUP BY g_c.name
HAVING g_c.name = 'Comedy';

CREATE TABLE query7 AS
SELECT avg(r_yr.rating) AS average
FROM ratings AS r_yr
WHERE r_yr.movieid IN((SELECT h_rb.movieid FROM genres AS g_yb, hasagenre AS h_rb WHERE g_yb.genreid = h_rb.genreid AND g_yb.name = 'Comedy'
INTERSECT
SELECT h_rb.movieid FROM genres AS g_yb, hasagenre AS h_rb WHERE g_yb.genreid = h_rb.genreid AND g_yb.name = 'Romance'));

CREATE TABLE query8 AS
SELECT avg(r_sj.rating) AS average
FROM ratings AS r_sj
WHERE r_sj.movieid IN((SELECT h_jk.movieid FROM genres AS g_sk, hasagenre AS h_jk WHERE g_sk.genreid = h_jk.genreid AND g_sk.name = 'Romance'
EXCEPT
SELECT h_jk.movieid FROM genres AS g_sk, hasagenre AS h_jk WHERE g_sk.genreid = h_jk.genreid AND g_sk.name = 'Comedy'));

CREATE TABLE query9 AS SELECT movieid, rating from ratings WHERE userid=:v1;
