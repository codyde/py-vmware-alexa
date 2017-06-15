param(
        [Parameter(Mandatory=$true)][String]$Operation
)

# https://chrisjwarwick.wordpress.com/2012/09/16/more-regular-expressions-regex-for-ip-v4-addresses/
Function ExtractValidIPAddress($String){
    $IPregex='(?<Address>((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))'
    if($String -Match $IPregex) {return $Matches.Address}
}

$configFile = "etc/config.txt"
$content = Get-Content $configFile

foreach ($line in $content) {
    if($line -match "url") {
        ($junk,$viurl) = $line.split("=")
        $viurl = $viurl.trim()
        $viurl = ExtractValidIPAddress($viurl)
    }
    if($line -match "user") {
        ($junk,$viuser) = $line.split("=")
        $viuser = $viuser.trim()
    }
    if($line -match "password") {
        ($junk,$vipassword) = $line.split("=")
        $vipassword = $vipassword.trim()
    }
}

Connect-VIServer -Server "$viurl" -User "$viuser" -Password "$vipassword" | Out-Null

switch($operation) {
    GetVCOS {
        $osType = $global:DefaultVIServer.ExtensionData.Content.About.osType
        Write-Host "$osType"
    }
}

Disconnect-VIServer * -Confirm:$false | Out-Null