UPDATE random_winners
SET count=count+1, last_win=date('now','localtime')
WHERE id={user_id}
