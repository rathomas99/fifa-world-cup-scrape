
#Query for a given cup
SELECT Cup.CupName as cn, Team.Name as tn, CupMember.Rank as r, tbl1.* 
FROM `Cup`
INNER JOIN `CupMember` on Cup.CupYear = CupMember.CupYear 
INNER JOIN `Team` on CupMember.TeamID=Team.TeamID
JOIN (SELECT g.TeamID, count(g.TeamID) 
FROM Goal `g`, CupMember `cm`,Game `gm` WHERE
g.gameID=gm.GameID
AND g.TeamID=cm.TeamID
AND gm.CupYear="""+str(inputvalue)+"""
group by g.TeamID) as tbl1 on tbl1.TeamID=Team.TeamID;


#Query for a given player
#Part 1: Find playerID
SELECT Player.PlayerID as pid FROM Player where Player.Name=value;
#Part 2:
SELECT tbl1.*,tbl2.gs 
FROM(
(SELECT Player.Name as pn,Team.Name, Cup.CupName, Cup.CupYear as cy, 
(Cup.CupYear-YEAR(Player.Birthday)) as age
FROM `Player`,`Team`,`Cup`,`TeamMember`,`CupMember`
WHERE TeamMember.PlayerID="""+str(pid)+"""
	AND Player.PlayerID=+"""+str(pid)+"""
	AND Team.TeamID=TeamMember.TeamID 
	AND CupMember.TeamID=Team.TeamID
    AND CupMember.TeamID=TeamMember.TeamID
	AND TeamMember.Year=CupMember.CupYear
    AND Cup.CupYear=CupMember.CupYear
    AND Cup.CupYear=TeamMember.Year) as tbl1;
JOIN 
	(SELECT gm.CupYear as cy2, count(gm.CupYear) as gs 
    FROM Goal `g`, Game `gm`,CupMember `cm`
	WHERE
    g.PlayerID="""+str(pid)+"""
    AND g.gameID=gm.GameID
	AND g.TeamID=cm.TeamID
	AND gm.CupYear=cm.CupYear
	group by gm.CupYear) as tbl2 on tbl1.cy=tbl2.cy2;


#Query For Super Stars
SELECT tbl1.*,tbl2.gs
FROM(
	(SELECT Cup.CupYear as cy,Player.Name as pname,Player.PlayerID as pid, 
    (Cup.CupYear-YEAR(Player.Birthday)) as age
	FROM `Player`,`Team`,`Cup`,`TeamMember`,`CupMember`
	WHERE  TeamMember.PlayerID=Player.PlayerID
		AND Team.TeamID=TeamMember.TeamID 
		AND CupMember.TeamID=Team.TeamID
		AND CupMember.TeamID=TeamMember.TeamID
		AND TeamMember.Year=CupMember.CupYear
		AND Cup.CupYear=CupMember.CupYear
		AND Cup.CupYear=TeamMember.Year
	GROUP BY Player.PlayerID HAVING Count(Player.PlayerID)>0)as tbl1

	JOIN 
		(SELECT g.PlayerID as pid2,gm.CupYear as cy2, count(gm.CupYear) as gs 
		FROM Goal `g`, Game `gm`,CupMember `cm`
		WHERE
		g.gameID=gm.GameID
		AND g.TeamID=cm.TeamID
		AND gm.CupYear=cm.CupYear
		group by g.TeamID) as tbl2 on tbl1.cy=tbl2.cy2 AND tbl1.pid=tbl2.pid2
);


#Team Historyical Query
#Part one get Team ID
SELECT Team.TeamID as tid FROM Team WHERE Team.Name="'"+value + "'";

#Part Two Get basic team data
SELECT Team.Name,Cup.CupName, CupMember.Rank, CupMember.CupYear 
FROM CupMember, Team, Cup
WHERE
	CupMember.CupYear=Cup.CupYear
    AND Team.TeamID=CupMember.TeamID
    AND Team.Name="'"+value+"'";

#Part 3 get goals 
SELECT tbl1.s2+tbl2.s1 FROM
(SELECT sum(gm2.Team1Score) as s2
FROM Game `gm2`
WHERE gm2.TeamID1="'"+str(tid)+"'")as tbl1,
(SELECT sum(gm.Team2Score) as s1
FROM Game `gm`
WHERE gm.TeamID2="'"+str(tid)+"'")as tbl2;

#Part 4 Get Goals recieved
SELECT tbl1.s2+tbl2.s1 FROM
(SELECT sum(gm2.Team2Score) as s2
FROM Game `gm2`
WHERE gm2.TeamID1="'"+str(tid)+"'")as tbl1,
(SELECT sum(gm.Team1Score) as s1
FROM Game `gm`
WHERE gm.TeamID2="'"+str(tid)+"'")as tbl2;

#Part 5
#Get Max Rank annd number of times participated
SELECT MAX(CupMember.rank),Count(*) 
FROM CupMember
WHERE CupMember.TeamID=tid;

#Query For CountrysPlayers
#For Every TeamID
SELECT tbl1.*, tbl2.*
FROM
(SELECT p.Name as pname,count(g.PlayerID) as penalty
FROM Goal `g`,Player `p`
WHERE g.TeamID="'"+str(TeamID)+"'" 
AND p.PlayerID=g.PlayerID AND g.Type='Penalty' 
GROUP BY g.PlayerID) as tbl1
RIGHT OUTER JOIN 
(SELECT p.Name as pname2,count(g.PlayerID) as regular
FROM Goal `g`,Player `p`
WHERE g.TeamID="'"+str(TeamID)+"'" 
AND p.PlayerID=g.PlayerID AND g.Type='Regular' 
GROUP BY g.PlayerID) as tbl2 on tbl2.pname2=tbl1.pname
UNION 
SELECT tbl1.*, tbl2.*
FROM
(SELECT p.Name as pname2,count(g.PlayerID) as regular
FROM Goal `g`,Player `p`
WHERE g.TeamID="'"+str(TeamID)+"'" 
AND p.PlayerID=g.PlayerID AND g.Type='Regular' 
GROUP BY g.PlayerID) as tbl2 
RIGHT OUTER JOIN 
(SELECT p.Name as pname,count(g.PlayerID) as penalty
FROM Goal `g`,Player `p`
WHERE g.TeamID="'"+str(TeamID)+"'" 
AND p.PlayerID=g.PlayerID AND g.Type='Penalty' 
GROUP BY g.PlayerID) as tbl1 on tbl2.pname2=tbl1.pname;



#Top 10 Venue Query
SELECT g.Venue, count(*)
FROM Game `g` 
GROUP BY g.Venue Order by count(*) DESC LIMIT 10;
