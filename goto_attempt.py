import PyIndi

# Connect to INDI server
indiclient = PyIndi.BaseClient()

def connect_to_telescope():
    # Connect to INDI server
    indiclient.setServer("cloud-1", 7624)
    if not(indiclient.connectServer()):
        print("Failed to connect to INDI server")
        return False

    # Wait for telescope device to be available
    telescope_device = None
    while not telescope_device:
        telescope_device = indiclient.getDevice("Telescope Simulator")
        if not telescope_device:
            print("Telescope device not found. Retrying...")
            indiclient.watchDevice("Telescope", True, True)

    # Set telescope device as the active device
    indiclient.setActiveDevice(telescope_device)

    return True

def move_telescope(ra, dec):
    # Get telescope property vectors
    ra_vector = indiclient.getVector("Telescope", "EQUATORIAL_EOD_COORD")
    dec_vector = indiclient.getVector("Telescope", "EQUATORIAL_EOD_COORD")

    # Set target coordinates
    ra_vector[0].value = ra
    dec_vector[0].value = dec

    # Send new coordinates to telescope
    indiclient.sendNewNumber(ra_vector)
    indiclient.sendNewNumber(dec_vector)

    # Wait for telescope to finish moving
    while (ra_vector[0].s == PyIndi.IPS_BUSY) or (dec_vector[0].s == PyIndi.IPS_BUSY):
        indiclient.sleep(1)

    # Check if telescope successfully moved
    if (ra_vector[0].s == PyIndi.IPS_OK) and (dec_vector[0].s == PyIndi.IPS_OK):
        print("Telescope successfully moved to coordinates: RA={}, DEC={}".format(ra, dec))
    else:
        print("Failed to move telescope to coordinates: RA={}, DEC={}".format(ra, dec))

# Connect to telescope
if connect_to_telescope():
    # Example coordinates: RA=10.123, DEC=20.456
    target_ra = 10.123
    target_dec = 20.456

    # Move telescope to target coordinates
    move_telescope(target_ra, target_dec)

