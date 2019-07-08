---
layout: default
title: GetBestBlockHash
parent: PAI Core Apis
grand_parent: Developer Reference
---

GetBestBlockHash
========================

The `getbestblockhash` RPC returns the header hash of the most recent block on the best block chain.

*Parameters: none*

*Result---hash of the tip from the best block chain*

{% include table_header.md
  n= "`result`"
  t= "string (hex)"
  p= "Required<br>(exactly 1)"
  d= "The hash of the block header from the most recent block on the best block chain, encoded as hex in RPC byte order"

%}

*Example*

Input:
```
paicoin-cli -regtest getbestblockhash
```

Result:
```
00000000018151b673df2356e5e25bfcfecbcd7cf888717f2458530461512343
```

*See also*

* `GetBlock`: gets a block with a particular header hash from the local block database either as a JSON object or as a serialized block.
* `GetBlockHash`: returns the header hash of a block at the given height in the local best block chain.

