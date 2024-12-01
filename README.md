# Music Festival Lineup Challenge

## DynamoDB Design Schema

The DynamoDB table was structured to optimize for the following queries:

1. **Retrieve all performances by a specific performer**: The primary key is set to the `Performer` attribute, allowing for quick lookups of all performances associated with a given artist.

2. **List all performances occurring within a given time range**: A Global Secondary Index is created on the `Date` as the partition key and `Start`as the sort key to facilitate efficient range queries. Although creating a secondary index increases the cost, when the number of records scale up, this would reduce the number of reads for the queries significantly. Therefore, if querying often is necessary, this schema is optimized by hashing to each date, and sorting them by the starting time for a time range.

To list all the performances occurring "fully" during a given time range, the query can be done as the following:

Choose a specific `Date`, query all performances with `Start` attribute lexicographically less than or equal to the chosen **start time**, and filter all performances with `End` attribute greater or equal to the chosen **end time** by the filter.


To list all the performances occurring "fully" or even "partially" during a given time range, the query can be done as the following:

Choose a specific `Date`, query all performances with `Start` attribute lexicographically less than or equal to the chosen **end time**, and filter all performances with `End` attribute greater than or equal to the chosen **start time** by the filter.

Although filtering is not-cost effective method, it is better than creating another GSI in this case because the secondary index already filtered the date and starting time, so there would not be as many records to filter through when filtering with the ending time.


3. **Fetch details for a specific performance given a stage and time**: A Global Secondary Index is created on the `Stage` as the partition key and `Date#Start` (combination of date and start time) as the sort key.

To query the details for a specific performance given a stage and time, choose the specific `Stage` for partition key, and get the specific performance with specific date and starting time `Date#Start` attribute.

If the time is not a starting time, then filtering can be used again because the data is reduced by the secondary index. The rationale for the GSI for the this query is similar to the rationale for the second query.


## Cost and Scalability Analysis

### Cost Estimation

S3 Bucket: Free tier - 5GB, $0.023 per GB
Lambda: Free Tier - 1M requests, $0.20 per 1M requests
Email SNS Notification: Free tier - 1,000 notifications, $2.00 per 100,000 notifications

Using on-demand throughput type, DynamoDB costs are the following:

Storage Cost: $0.25/GB 
Write Request Units (WRU): $0.625 per million write request units
Read Request Units (RRU): $0.125 per million read request units

- **1,000 Daily Records**: 30,000 Records monthly. Estimated cost is minimal, as DynamoDB's free tier covers a significant portion of this usage. S3, lambda and SNS costs are trivial, because they are very little:

Assuming that 100 records/CSV file, it is 300 notifications per month, so S3, Lambda and SNS are all covered by the free tier. 

DynamoDB Cost:

30,000 Records / 100 Records x 5KB = 150KB
150KB = 0.00015GB x $0.25 = $0.00/month
Storage Cost: $0.00/month

Assuming you write 100 lines of CSV data for each file submission:

5KB / 1KB = 5 WRU/file (100 Records)
5 WRU/file x 300 x 3 (main table and 2 GSI) = 4500 WRU/month (30,000 Records)
Write Cost = $0.01

Asssuming only eventually consistent reads, and you run 100 queries/day (underestimation):

150KB / 4KB = 37.5 = 38 RCU (1 Scan Query)
38 RCU x 3,000 Queries/month = 114,000 RCU
Read Cost = $0.01

Therefore, the total cost is only $0.02.


- **10,000 Daily Records**: 300,000 Records monthly.
Assuming that 100 records/CSV file, it is 3,000 notifications per month, so S3, Lambda are covered by free tier, SNS is $0.04. 

DynamoDB Cost:

300,000 Records / 100 Records x 5KB = 1500KB
1500KB = 0.0015GB x $0.25 = $0.00/month
Storage Cost: $0.00/month

Assuming you write 100 lines of CSV data for each file submission:

5KB / 1KB = 5 WRU/file (100 Records)
5 WRU/file x 3000 x 3 (main table and 2 GSI) = 45000 WRU/month (300,000 Records)
Write Cost = $0.14/month

Asssuming only eventually consistent reads, and you run 100 queries/day (underestimation):

1500KB / 4KB = 375 RCU (1 Scan Query)
375 RCU x 3,000 Queries/month = 1,125,000 RCU
Read Cost = $0.14

Therefore, the total cost is only $0.32.


- **100,000 Daily Records**: 3,000,000 Records monthly.
S3 and Lambda are still under the free tier limit, and SNS calls 30,000 email notifications per month, so the cost is $0.58.

DynamoDB Cost:

3,000,000 Records / 100 Records x 5KB = 15000KB
15000KB = 0.015GB x $0.25 = $0.00/month
Storage Cost: $0.00/month

Assuming you write 100 lines of CSV data for each file submission:

5KB / 1KB = 5 WRU/file (100 Records)
5 WRU/file x 30000 x 3 (main table and 2 GSI) = 450000 WRU/month (3,000,000 Records)
Write Cost = $1.41/month

Asssuming only eventually consistent reads, and you run 100 queries/day (underestimation):

15000KB / 4KB = 3750 RCU (1 Scan Query)
3750 RCU x 3,000 Queries/month = 11,250,000 RCU
Read Cost = $1.41

Therefore, the total cost is still only $3.40.

### Scalability Strategies
Even though I estimated the queries to be only 100 per day, and I did not account for the cumulative data size for calculating RRU, the cost of the write with 2 GSI's were equal to the read cost with 100 scan queries per day. Therefore, optimizing DynamoDB schema with GSI's is more efficient choice than filtering the whole table, especially when the size of the table scales up.

Also, choosing provisioned throughput would be a good for larger number of records than on-demand mode. TThe number of records to work with have a steady and predictable growth, so based on the number of daily records, the provisioned read and write capacity can be set so that needlessly larger read and write are prevented. 
