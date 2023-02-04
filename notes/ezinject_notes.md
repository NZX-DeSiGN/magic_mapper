## Locate services
find . -name comm | grep -v task | xargs -I {} grep -E 'RELEASE|tvservice|micomservice|lginput2|testapp' {} /dev/null

    ./1586/comm:tvservice

## Inject
/ezinject target['pid'] '/libphp.so ' + dir + '/lginput-hook.php ' + target[1] +	' > /tmp/ezinject-' + target[1] + '.log 2>&1');
