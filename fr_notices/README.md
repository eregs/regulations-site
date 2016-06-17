# FR Notices

While developing the notice-and-comment portion of eRegs, we initially put all
new functionality within the `regulations` app. Given the complexity of the
functionality, we added significant code debt. As a small step towards
combating that debt, we've created this (in-progress) `fr_notices`
library/Django app.

The ultimate goal is to separate CFR-viewing components from Notice-viewing
and commenting components. Along the way, we can refactor and modularize large
swaths of the notice-and-comment code which had been shoved into a small
number of libraries. In particular, the following modules should be moved into
this lib/sub-app:

* regulations.views.preamble
* regulations.views.comment
* regulations.models
* regulations.docket
* templates associated with the above
* URL mappings associated with the above
