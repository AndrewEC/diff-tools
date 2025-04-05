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

. ./build-scripts/Activate.ps1
. ./build-scripts/Audit.ps1
. ./build-scripts/Flake.ps1
. ./build-scripts/Install.ps1
. ./build-scripts/Test.ps1

Invoke-ActivateScript

switch ($ScriptAction) {
    "All" {
        Invoke-InstallScript
        Invoke-FlakeScript
        Invoke-TestScript 80 {
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
