@echo off
powershell -ExecutionPolicy Bypass -NoProfile -Command "try { $d=Invoke-RestMethod -Uri 'https://wttr.in/Beijing?format=j1' -TimeoutSec 15; $t=$d.weather[1]; $out=('Tomorrow ('+$t.date+') Beijing: '+$t.hourly[4].weatherDesc[0].value+'`nTemp: '+$t.mintempC+' ~ '+$t.maxtempC+' C') } catch { $out=('ERROR: '+$_) }; $out | Out-File -FilePath 'E:\test\weather-result.txt' -Encoding UTF8"
notepad "E:\test\weather-result.txt"
