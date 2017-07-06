# Orbeon - Integrate Orbeon Forms with Odoo

## General information

General information is available online:

- [About this Odoo App](https://www.odoo.com/apps/modules/10.0/orbeon)
- For more information about Orbeon Forms visit [orbeon.com](http://www.orbeon.com)


## Installation

Some system administration (with root access) is required.

### 1. Orbeon Forms

#### 1.1 Get and install Orbeon Forms

Orbeon Forms is a Java (web)application. It has extensive [documentation](https://doc.orbeon.com/installation)

#### 1.2 Configure Orbeon Forms to connect with Odoo

*The Orbeon Persistence configuration*

Orbeon Forms is configured via *configuration properties*.<br/>
For more info visit https://doc.orbeon.com/configuration/properties/


**Open or create the Orbeon properties file:**
```
<ORBEON-ROOT-DIR>/WEB-INF/resources/config/properties-local.xml
```

For example, if Orbeon is deployed by Tomcat: 

```
/var/lib/tomcat8/webapps/<ORBEON>/WEB-INF/resources/config/properties-local.xml
```

**Ensure the following properties are set:**

Property | Explanation
-------- | -----------
```oxf.fr.persistence.provider.odoo.*.form ``` | Form definitions for all forms in application "odoo".
```oxf.fr.persistence.provider.odoo.*.data ``` | Form data for all forms in application "odoo".
```oxf.fr.persistence.odoo.uri``` | Specifies the location, via HTTP, of the provider implementation. In this case the Odoo host with a specific configured **port** in the (Odoo) ["Orbeon Server"][odoo-orbeon-server] (see section **2.4** below).

**Configuration example:**

  ``` xml
  <property 
      as="xs:string"
      name="oxf.fr.persistence.provider.odoo.*.form"
      value="odoo"/>
      
  <property 
      as="xs:string"
      name="oxf.fr.persistence.provider.odoo.*.data"
      value="odoo"/>
  
  <property as="xs:anyURI"
      name="oxf.fr.persistence.odoo.uri"
      value="http://localhost:8090"/>
  ```

### 2. Odoo - Orbeon App

#### 2.1 Get this App

Put it in your Odoo addon-path.

1. [Download from the Odoo Apps site](https://www.odoo.com/apps/modules/10.0/orbeon)
2. "Git clone" the repository and checkout the Odoo version branch. This provides simpler updates for the "Git savvy".

#### 2.2 Python dependencies

Install the required Python libraries. (Also required for the unittests)

```pip install -r requirements.txt```

#### 2.3 Install the Orbeon App

Just install it in Odoo like any regular Odoo App.

#### 2.4 Create Orbeon Server

[odoo-orbeon-server]: #odoo-orbeon-server

1. Via the Odoo main menu, go to: *Orbeon > Server*
2. Click *Create* and fill in the following form fields:

Section  | Field | Description
-------- | ----- | ------------
Orbeon Server | **Name** | A descriptive name
Orbeon Server | **URL** | URL to the Orbeon Forms Application, e.g: http://localhost:8080/orbeon
Orbeon Server | **Description** | Anything (not mandatory)
Orbeon Persistence Server | **Port** | An available (Unix/Linux) port
Orbeon Persistence Server | **Process-type** | WSGI/Webserver process type
Orbeon Persistence Server | **Config-file path** | Odoo connection settings and such; See [configfile][configfile] Especially easy for developers. Or in case there's no Webserver in front yet - with authentication via HTTP-headers.
Orbeon Persistence Server | **Autostart** | Whether the Orbeon Server connection automatically starts when Odoo server starts
Orbeon Persistence Server | **Active** | State of the Server and configuration, so it can't be started anyway.

#### 2.5 Config File "Odoo Persistence Server"

Configuration example

  - **server_url**: Connect to Odoo server on 'localhost'
  - **port**: Odoo port e.g. '8069'
  - **database_name**: The Odoo database e.g. 'odoo'
  - **username**: An 'odoo' user account with at least one of groups **Orbeon User**, **Orbeon Admin**
  - **password**: Password of the 'odoo' user account

```
[odoo config]
server_url: http://localhost
port: 8069
database_name: odoo
username: orbeon
password: orbeon
```

#### 2.6 Start the Odoo Orbeon Server

If everyting is setup correctly, you're now able to use Orbeon Forms via Odoo.

In case of failure or questions, first check the *Odoo server log* or the *Java Webserver log*.
