param(
    [ValidateSet(
        "All",
        "Audit",
        "Flake",
        "Install",
        "Tests"
    )]
    [string]$ScriptAction
)

Import-Module ./PyBuildScripts

Invoke-ActivateScript

switch ($ScriptAction) {
    "All" {
        Invoke-InstallScript
        Invoke-FlakeScript
        Invoke-TestScript 75 {
            coverage run `
                --omit=./diff/tests/* `
                --source=diff.core `
                --branch `
                --module diff.tests.__run_all
        }
        Invoke-AuditScript
    }
    "Audit" { Invoke-AuditScript }
    "Flake" { Invoke-FlakeScript }
    "Install" { Invoke-InstallScript }
    "Tests" {
        Invoke-TestScript 75 {
            coverage run `
                --omit=./diff/tests/* `
                --source=diff.core `
                --branch `
                --module diff.tests.__run_all
        }
    }
}
