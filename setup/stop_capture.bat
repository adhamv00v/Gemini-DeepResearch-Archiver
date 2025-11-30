\
        @echo off
        echo Stopping mitmproxy...
        taskkill /IM mitmweb.exe /F
        taskkill /IM mitmdump.exe /F
        echo Done.
