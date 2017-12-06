db.Coppertone.aggregate(

	// Pipeline
	[
		// Stage 1
		{
			$group: {
			  
			  "_id": {"hour": { $hour: "$status_published" }},   
			  "count": {"$sum":1}
			         
			}
		},

	]

	// Created with Studio 3T, the IDE for MongoDB - https://studio3t.com/

);

