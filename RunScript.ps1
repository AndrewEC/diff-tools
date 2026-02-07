param(
    [ValidateSet(
        "All",
        "Audit",
        "Lint",
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
        Invoke-RuffScript
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
    "Lint" { Invoke-RuffScript }
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
