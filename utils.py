from ldap3 import Server, Connection, ALL, MODIFY_ADD, MODIFY_REPLACE, MODIFY_DELETE
import os
import logging 

def check_user(cx_method="ldap", user=None, auth_token=None):
    if user is None:
        return {"user": "Not found", "success": False, "message": "User was not set"}
    elif auth_token is None:
        return {"user": "Not found", "success": False, "message": "Auth token was not set"}
    else:
        if cx_method == "ldap":
            ldap_server = Server(os.getenv("LDAP_SERVER_URI"), get_info=ALL)
            ldap_connection = Connection(ldap_server, os.getenv("LDAP_SERVER_USER"), os.getenv("LDAP_SERVER_PASS"))
            cx = ldap_connection.bind()
            logging.info("Bound to server as admin user")
            logging.info(f"Checking LDAP Server for {user.properties['firstname']} {user.properties['lastname']}")
            result = ldap_connection.search('ou=people,dc=auth,dc=makemonmouth,dc=co,dc=uk',
                              f"(email={user.properties['email']})",
                              attributes=['objectclass', 'memberOf'])

            if result is False:
                logging.warning(f"User {user.properties['firstname']} {user.properties['lastname']} not found in LDAP, creating")
                if user.properties['membership_level'] is not None:
                    ldap_connection.add(
                            f"cn={user.properties['firstname'].lower()}.{user.properties['lastname'].lower()},ou=people,dc=auth,dc=makemonmouth,dc=co,dc=uk",
                            "inetOrgPerson",
                            {
                                "firstname": user.properties['firstname'],
                                "lastname": user.properties['lastname'],
                                "email": user.properties['email'],
                                "memberOf": [f"cn={user.properties['membership_level'].lower()},ou=groups,dc=auth,dc=makemonmouth,dc=co,dc=uk"],
                            }
                            )
                else:
                    ldap_connection.add(
                            f"cn={user.properties['firstname'].lower()}.{user.properties['lastname'].lower()},ou=people,dc=auth,dc=makemonmouth,dc=co,dc=uk",
                            "inetOrgPerson",
                            {
                                "firstname": user.properties['firstname'],
                                "lastname": user.properties['lastname'],
                                "email": user.properties['email'],
                            }
                            )
            else:
                logging.debug("User found in database, checking group membership")
                for group in ldap_connection.entries[0].memberOf:
                    print(group)
        
        elif cx_method == "graphql":
            """ 

            Graph QL Method for LLDAP

            """
            from gql import gql, Client
            from gql.transport.requests import RequestsHTTPTransport

            # Set the headers
            headers = {
                    "Authorization": f"Bearer {auth_token}"
                    }
            # Select your transport with a defined url endpoint
            transport = RequestsHTTPTransport(url=os.getenv("GQL_SERVER_URI"), headers=headers)

            # Create a GraphQL client using the defined transport
            client = Client(transport=transport, fetch_schema_from_transport=True)

            # Provide a GraphQL query
            get_user_query = f"""
            query {{
                users(filters: {{
                    eq: {{
                        field: "email"
                        value: "{user.properties['email']}"
                   }}
                }})
              {{
                id, email, groups {{
                    id, displayName
                    }}
              }}
            }}
            """
            get_group_query = """
            query {
                groups{
                    id, displayName
                }
            }
            """
            user_query = gql(get_user_query)
            group_query = gql(get_group_query)

            # Execute the query on the transport
            user_query_result = client.execute(user_query)
            if len(user_query_result['users']) > 0:
                user_query = user_query_result['users'][0]
                group_result = client.execute(group_query)['groups']

                membership_is_correct = False
                current_groups = []
                for group in user_query['groups']:
                    current_groups.append(group['displayName'])

                if user.properties['membership_level'] is not None:
                    if user.properties['membership_level'].lower() not in current_groups:
                        logging.debug(f"{user.properties['membership_level']} not found for {user_query['id']}")
                        target_group = "guest"
                        for group_data in group_result:
                            if group_data['displayName'] == user.properties['membership_level'].lower():
                                logging.debug(f"Found group {user.properties['membership_level'].lower()} in directory, adding user to it")
                                mod_query_string = f"""
                                    mutation {{
                                      addUserToGroup(userId: "{user_query['id']}", groupId: {group_data['id']}){{
                                        ok
                                      }}
                                    }}
                                """
                                mod_query = gql(mod_query_string)
                                mod_result = client.execute(mod_query)

            else:
                create_user_query = f"""
                  mutation {{
                      createUser(user: {{
                        id: "{user.properties['firstname']}.{user.properties['lastname']}"
                        email: "{user.properties['email']}"
                        displayName: "{user.properties['firstname']} {user.properties['lastname']}"
                        firstName: "{user.properties['firstname']}"
                        lastName: "{user.properties['lastname']}"
                      }}
                      ){{
                        id
                        displayName
                        email
                      }}
                    }}
                    """
                create_user_gql = gql(create_user_query)

                create_user = client.execute(create_user_gql)

                            

            return user_query
