# victoria_pbi

The Victoria PBI plugin is used for manipulating Azure DevOps PBIs.

## Usage

### Prerequisites
- Python 3.7+
- Pip
- Victoria

### Installation
```terminal
$ pip install git+https://glasswall@dev.azure.com/glasswall/Glasswall%20Cloud/_git/Glasswall.SRE.Victoria.PBI
```

### Config
The PBI plugin requires the following section in your Victoria config:

```yaml
plugins_config:
  pbi:
    access_token: An Azure DevOps access token
    organisation: glasswall
    project: Glasswall Cloud
    email: sgibson@glasswallsolutions.com
```

- `access_token`: Create a new access token with full access as-per 
  [this guide](https://docs.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops)
- `organisation`: Your Azure DevOps organisation. Find it in your Azure DevOps
  URL: `https://dev.azure.com/{organisation}/`.
- `project`: The project to scope to in Azure DevOps. Find it in your Azure
  DevOps URL: `https://dev.azure.com/{organisation}/{project}`.
- `email`: Your email that you use with Azure DevOps. This will be used in the
  `ls` command as the default user to get PBIs assigned to.

### Help text
```
Usage: victoria pbi [OPTIONS] COMMAND [ARGS]...

  Manipulate Azure DevOps PBIs.

Options:
  -h, --help  Show this message and exit.

Commands:
  assign   Assign work item(s) to someone by IDs and USER.
  boards   List boards.
  columns  List BOARD columns.
  get      Get work item(s) by ID.
  ls       List work items.
  mv       Move work item(s) by IDs to a different COLUMN.
```

### Examples
- List Azure DevOps boards
    - `victoria pbi boards`
- List Azure DevOps board columns
    - `victoria pbi columns "Glasswall DevOps Team"`
- List work items assigned to you
    - `victoria pbi ls`
- List work items assigned to someone else
    - `victoria pbi ls apotter-dixon`
    - or with email, `victoria pbi ls apotter-dixon@glasswallsolutions.com`
- Get work items by ID
    - `victoria pbi get 100178 99984`
- Assign some work items to someone
    - `victoria pbi assign 100178 99984 sgibson`
- Move some work items to another column
    - `victoria pbi mv 100178 99984 "On Hold"`

## Development

### Prerequisites
- Python 3.x
- Pipenv

### Quick start
1. Clone this repo.
2. Run `pipenv sync`
3. You're good to go. You can run commands using the package inside a
   `pipenv shell`, and modify the code with your IDE.
   