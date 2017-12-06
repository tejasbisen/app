db.CopComments.aggregate(
[
  {$group: { "_id" : {
    year:{$year:"$comment_published"}
    },
    count:{$sum: 1 }
  }
}
])