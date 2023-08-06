=========
Changelog
=========

------------------
0.5.1 - 2013-11-22
------------------

* Bug Fix: Corrected the handling of application/x-www-form-urlencoded
  for the signature verification.  [PMR/pmr2.oauth#4]

----------------
0.5 - 2013-10-24
----------------

* Updated the supported oauthlib to 0.6.0
* The design has been refactored to rely on the token endpoint classes
  for the validation.
* Support OAuth requests encoded using URL query strings.
* Addition of new content types into portal should no longer result in
  z3c.form-3.0.0 breaking on <NO_VALUE>.
* Updated a large amounts of text and even an internal management
  endpoint to be more clear and reflective of the terminology used in
  RFC 5849.
* More usability fixes.  The entire management interface should now be
  easily accessible through the Site Setup menu, and also the inner
  management pages should link back to the main OAuth management page.

------------------
0.4.5 - 2013-07-09
------------------

* Removed deprecated imports from zope.app.*.

------------------
0.4.4 - 2013-04-04
------------------

* URL encoding/decoding workaround to ensure the query parameters are
  being processed correctly.
* Bug fix: Deleting a client (consumer) no longer prevents user from
  managing their list of issued tokens.
* Depends on oauthlib 0.4.0

------------------
0.4.3 - 2013-02-01
------------------

* Pin the minimum supported oauthlib version to 0.3.5 to maintain
  consistency of the require_callback parameter.

------------------
0.4.2 - 2013-01-31
------------------

* Security Fix: Correctly apply CSRF protection to all forms.
* Denying a non-existent token will no longer show a stack trace.

Note: 0.4.1 was aborted due to incomplete fix.

----------------
0.4 - 2013-01-22
----------------

~~~~~~~~~~~~~~~~~~~~~~~~~~~
Major architectural changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Removal of python-oauth2 and use oauthlib.  Significant changes to the
  PAS OAuthPlugin, including the removal of all private methods,
  replacement of the OAuthUtility with an adapter, with nearly all
  authentication and verification functions moved into this adapter,
  which extends the oauthlib server class.
* Scope manager completely redefined to accept any identifiers, which
  can be client (consumer), temporary or access keys.  Specific
  implementations can then make use of this change.
* Default scope manager no longer manages permitted URIs based directly
  on regex, but views and subpaths within specific content types.
* Consumer keys now randomly generated.  For identification purposes the
  title and domain fields are introduced.  Domain field serves an
  additional purpose for verification of callbacks by the default
  callback manager.

~~~~~~~~~~~~
New features
~~~~~~~~~~~~

* Introduction of callback manager.  This manages permitted targets for
  callbacks, so that resource owners will not be redirected to untrusted
  hosts especially for oob clients.
* Default scope manager provides the concept of scope profiles, which
  are concise representations of access that will be granted by the
  resource owner to clients.
* Base classes for extending/replacing provided functionalities.
* An index of all valid endpoints (views) made available by this add-on.

~~~~~~~~~~~~~~~~~~~~~~
Bugs (and maybe fixes)
~~~~~~~~~~~~~~~~~~~~~~

* The missing permissions.zcml is now included.  (noted by ngi644)
* Translations are not included with this release as there were too many
  new and modified text.

-----------------
0.3a - 2012-11-23
-----------------

* Scope manager now permit POST requests.
* Corrected the scope verification to be based on the resolved internal
  script URL.
* Corrected the signature verification method to use the actual URL, not
  the internal script URL.
* Workaround the adherence to legacy part of the spec in python-oauth2.

Note: This is a special release for development of PMR2-0.7 (or Release 
7), as this package now depends on some packages not yet released.  This
release is made regardless as it is needed for demonstration purposes.

----------------
0.2 - 2012-10-16
----------------

* Completing i18n coverage and added Italian support.  [giacomos]
* Added intermediate form class to eliminate the need to define wrapper
  classes for compatibility between Plone and z3c.form.

----------------
0.1 - 2011-10-20
----------------

* Provide the core functionality of OAuth into Zope/Plone, through the
  use of custom forms and the Pluggable Authentication System.
* Contain just the basic storage for all associated data types, but
  extensibility is allowed.
