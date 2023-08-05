TAHOE
=====

A light layer on top of Flask that handles the drudgery you'd end up writing anyway as your app gets to a production state.

A lot of this is just best practices as explained in the Flask, SQLAlchemy, and related library documentation with a little bit of experience gleaned from running large Flask applications on the Obama Campaign and in using this code to run and power an API for a popular iPhone application we contracted for.

Currently we're making heavy use of this framework at Lunar internally and hopefully publicly soon!

Installation
============

Add the following line to your project's pip requirements file:

```
tahoe==1.0
```

This will pin your install at the v1.0 tag. To manually install, use pip:

```
pip install tahoe==1.0
```


Usage
=====

There is not too much documentation yet, but there are tests so those should be pretty illustrative.

To use you just import the bits you need, like:

```
from tahoe.models import ModelRegistry
```

```
from tahoe.encoding import json_loads, json_dumps
```

```
from tahoe.models.mixins import SearchableMixin, TimestampableMixin
```

And so on. Contact Clint Ecker <clint@ltc.io> for any questions on usage, buxfixes, comments, et cetera.

License
=======

Tahoe is licensed under the MIT License. See [the LICENSE file](LICENSE) for more information.

Lunar Technology Corp
=====================

Lunar is dedicated to building the future of commerce. We are a small team in Chicago, IL that is focusing on making purchasing easy for everyone.

Our team has been responsible for hundreds of millions of dollars of revenue flowing through fast and scalable systems. We are now bringing that experience to the mobile consumer.

Ready?

---

If this sounds interesting, we are constantly looking for the best people in the world to join our team.

Email [jobs@ltc.io](mailto:jobs@ltc.io) if you are ready.
