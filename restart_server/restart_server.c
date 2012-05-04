#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <unistd.h>

int main(int argc, char **argv) {

    char buffer[75];

    sprintf(buffer, "/usr/local/bin/restart_server.py %s", argv[1]);

    printf("Running command: %s\n\n", buffer);

    setuid(0);
    system(buffer);

    return 0;
}
