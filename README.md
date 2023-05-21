# Hubspot LDAP Sync

This tool acts as a lightweight sync service between [Hubspot.com](https://www.hubspot.com/) and an LDAP server.

By default, it is setup to use the excellent [LLDAP](https://github.com/lldap/lldap) via GraphQL, however the code exists to create new users in a "standard" LDAP server and Pull Requests are welcome to improve on this.

## Using the tool

   * In Hubspot, create a custom field named "Membership Level" and add the appropriate values.
      * You must have at least `None` and one other value in this box for the script to work, we have `None`, `Guest`, `Supporter`, and `Member`
   * In your LDAP server, create one group for each of the "other" values you've added to Hubspot, making sure they are all lower-case.
   * Copy `env.sample` to `.env` and change the values to suit your username/password.
   * Install the dependencies using `poetry install` (this uses the [Poetry](https://python-poetry.org/) package manager)
   * Run the script using `poetry run python ldapsync.py`

You should then see the members pulled in to LDAP and assigned to the appropriate group in the LLDAP web interface.

### Using Docker

There is a `Dockerfile` available if you want to build and run this as a container.  We hope to do more work on this in the near future and publish it properly, however if you need support in the meantime please raise an issue.


