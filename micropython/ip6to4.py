

def ipv6_to_embedded_ipv4(ipv6_addr):
    try:
        # Parse the IPv6 address
        ipv6_obj = ipv6_addr
        
        # Extract the next 4 bytes after 2002:
        ipv4_bytes = ipv6_obj.packed[2:6]
        
        # Convert to dotted-decimal IPv4
        ipv4_addr = ".".join(str(b) for b in ipv4_bytes)
        return ipv4_addr
    except ValueError:
        return None

if __name__ == "__main__":
    while 1:
        ipv6_input = input("Enter a 6to4 IPv6 address: ")
        ipv4_result = ipv6_to_embedded_ipv4(ipv6_input)
        if ipv4_result:
            print(f"Embedded IPv4: {ipv4_result}")
        else:
            print("Not a valid 6to4 IPv6 address.")
