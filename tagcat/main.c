#include <errno.h>
#include <inttypes.h>
#include <signal.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

#include <nfc/nfc.h>
#include <nfc/nfc-types.h>

#define POLL_PERIOD 100
#define IDLE_TIME 300

static nfc_context *context = NULL;
static nfc_device *device = NULL;

static volatile sig_atomic_t stop = 0;

static void sigint_handler(int signum)
{
    stop = 1;
}

static void die(const char *format, ...)
{
    va_list va;

    va_start(va, format);

    vfprintf(stderr, format, va);
    fprintf(stderr, "\n");
    fflush(stderr);

    va_end(va);

    exit(EXIT_FAILURE);
}

static void delay(int milliseconds)
{
    while (true)
    {
        if (usleep(milliseconds * 1000) != 0)
        {
            if (errno == EINTR)
            {
                continue;
            }

            die("Call `usleep` failed");
        }

        return;
    }
}

static void cleanup(void)
{
    if (device != NULL)
    {
        nfc_close(device);
    }

    if (context != NULL)
    {
        nfc_exit(context);
    }
}

int main(int argc, char **argv)
{
    if (atexit(cleanup) != 0)
    {
        die("Call `atexit` failed");
    }

    struct sigaction sa;

    sa.sa_handler = sigint_handler;
    sa.sa_flags = SA_RESTART;

    if (sigemptyset(&sa.sa_mask) != 0)
    {
        die("Call `sigemptyset` failed");
    }

    if (sigaction(SIGINT, &sa, NULL) != 0)
    {
        die("Call `sigaction` failed");
    }

    nfc_init(&context);

    if (context == NULL)
    {
        die("Call `nfc_init` failed");
    }

    device = nfc_open(context, NULL);

    if (device == NULL)
    {
        die("Call `nfc_open` failed");
    }

    if (nfc_initiator_init(device) != 0)
    {
        die("Call `nfc_initiator_init` failed");
    }

    while (stop == 0)
    {
        nfc_target target;

        const nfc_modulation modulation = { .nmt = NMT_ISO14443A, .nbr = NBR_106 };
        int res = nfc_initiator_list_passive_targets(device, modulation, &target, 1);

        if (res < 0)
        {
            die("Call `nfc_initiator_list_passive_targets` failed");
        }
        else if (res == 1)
        {
            if (target.nti.nai.szUidLen > 32)
            {
                die("Target UID length too big (%" PRIu32 " bytes)", target.nti.nai.szUidLen);
            }

            for (size_t i = 0; i < target.nti.nai.szUidLen; i++)
            {
                fprintf(stdout, "%" PRIx8, target.nti.nai.abtUid[i]);
            }

            fprintf(stdout, "\n");
            fflush(stdout);

            while (nfc_initiator_target_is_present(device, NULL) == 0)
            {
                delay(POLL_PERIOD);
            }

            delay(IDLE_TIME);

            continue;
        }

        delay(POLL_PERIOD);
    }

    exit(EXIT_SUCCESS);
}
