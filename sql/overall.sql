SELECT id, count FROM random_winners
WHERE count>0
ORDER BY count DESC
LIMIT 10;
