

Extract data from digis:

```
zapi query -I fuse.zed -o lamps.zng
```

===


In this demo, Amy and I are going to present Zed in action. You will see how the hybrid data model supports data formats for different purposes. How they convert to each other without lossing any data or type information. Also how we can perform search, analytics, and data discovery effectively on the hybrid data model. Here we are going to use a simple IoT dataset which contains the timeseries about 3 lamps from 3 different vendors. 

Let's begin by taking a look at the dataset. To do so, we run:

```
zq lamps.zng
```

The default format here is zng. Which is convienient to store IoT data that are sent or streamed in row by row. Here, the first thing we notice is that storing data in Zed format is as easy as storing data with JSON, where records with different schema can coexist in the same file (for example, this lifx lamp and this geeni records, which have different schema). And the data are self-describing, meaning its type or schema information are stored inline with the data.

But notice that unlike JSON, ZNG is binary format. It's much more compact than JSON and hence more storage efficient. 

```
# To see this let's we compare their file sizes. lamps.ndjson this somethign we prepared beforehand
 ls -lh lamps.ndjson lamps.zng
```

Here we have about 620 kilobytes of data in JSON but only 66  kilobytes in ZNG, which is about 10x smaller.

Now, while our command line Zq is able to parse the ZNG format and present it in a human readable way, as we said the ZNG format itself is not human readable, it's a binary format. For human readability, Zed provides another format ZSON:

```
# So let's convert ZNG to ZSON:
zq -f zson -o lamps.zson lamps.zng
head -6 lamps.zson
```

```
# In fact, we can use zq to show us ZSON format directly.
zq -Z "head" lamps.zng
```

Here you may wonder, isn't ZSON just JSON? They look very much alike! Well, you are absolutely right that here they would indeed look identical. In fact, ZSON is intended as a literal superset of JSON syntax. This simple IoT dataset contains types that were in JSON and as we see ZSON can fully express these data records, and share the look and feel of JSON.

However, underneath ZSON's design, it differs substantially from JSON:

```
# For example, let's take a quick look at a more complex dataset in network logs
zq -Z "head" conn.zson
```

As can be seen, ZSON has a much more comprehensive type system than JSON. It supports first class types as Amy explained and I will demo later. And what's more, ZSON and ZNG they are semantically-matched, which means we can convert ZSON and ZNG losslessly between each other with ZNG being a much more compact and performant binary format. And so does ZST. 

Specifically,

Besides ZNG and ZSON, Zed offers a columnar format ZST which Amy described previsouly. Now, what's unique about the hybrid data model is that all three formats, ZNG, ZST, and ZSON, they can convert to each other losslessly. 

```
# To see this, let's fiorst we convert ZNG to ZST:
zq -f zst -o lamps.zst lamps.zng
```

```
# Then, let's convert ZST back to ZNG: 
zq -i zst -f zng -o lamps-from-zst.zng lamps.zst
sha1sum lamps.zng && sha1sum lamps-from-zst.zng
```
As you can see,  their hashes are identical. Meaning, format conversions under the hybrid data model do not alternate any information about the data. So the type and record ordering all stay the same.

The same is not true with existing formats such as converting Parquet, which is a popluar columnar format, to JSON and back:
```
sha1sum lamps.parquet && sha1sum lamps-from-ndjson.parquet
```
So the two parquet files have different content.

Now before we move on to queries, one more thing I want show here is that, with Zed, because data are self-describing, we can easily append new records with different schema to the same file. 
```
echo '{power:"on",watt:"12",vendor:"tuya",ts:"2021-12-02T00:21:02.149812Z"}' >> lamps.zson

# And it works just fine.
zq -Z 'tail' lamps.zson
```

Now let's do some simple queries. Let's start with search. Say we want to get the records where the lamps' are power on.

```
zq -Z 'power=="on"' lamps.zng
```

Or we want to get all the records from a particular vendor.
```
zq -Z 'vendor=="tuya"' lamps.zson
```

Besides doing search, performing analytics on Zed data is also straightforward. Say we want to calculate the average brightness of all lamps.

```
zq -Z 'avg(brightness)' lamps.zson
```

Now you may wonder,  we should only consider the brightness for lamps whose power are on. Well, in Zed one can easily combine search and analytics, for instance:

```
zq -Z 'power =="on" | avg(brightness)' lamps.zson
```

Another key feature of Zed is, as Amy mentioned, that in Zed, type is first-class. This means we can treat types as data and perform data discovery easily.

For example, we can count the number of records per type:

```
zq -Z 'count() by typeof(this)' lamps.zson
```

Here it shows the count of the four different schema from the four different vendors.

We can return sample records that are grouped by type:

```
zq -Z 'any(this) by typeof(this)' lamps.zson
```

And we can even search or filter records by type:

```
zq -Z 'is(type({power:string,brightness:float64,color:string,vendor:string,ts:string}))' lamps.zson
```

This is the end of the demo. Hopefully you get sense of the ergonomics that Zed enables in doing analytics, search, and data discovery, which are all made possible with the hybrid data model.

```
time zq -i zst "sum(orig_bytes)" conn.zst
time zq -i zng "sum(orig_bytes)" conn.zng
```