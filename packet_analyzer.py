from scapy.all import sniff, IP, TCP, UDP, ICMP
from datetime import datetime
from collections import Counter


# ============================================================
# NETWORK PACKET ANALYZER
# A simple Python-based network monitoring project
# ============================================================


# -------------------- Global Variables ---------------------

packet_count = 0
total_bytes = 0

protocol_count = Counter()


# -------------------- Display Header -----------------------


def display_header():
    print("\n")
    print("=" * 75)
    print("                 NETWORK PACKET ANALYZER")
    print("=" * 75)
    print("  Live Network Traffic Monitoring using Python + Scapy")
    print("=" * 75)
    print()


# -------------------- Analyze Packet -----------------------


def analyze_packet(packet):
    global packet_count
    global total_bytes

    # Analyze only packets containing IP information
    if IP not in packet:
        return

    packet_count += 1

    # Get packet size
    packet_size = len(packet)
    total_bytes += packet_size

    # Get time
    current_time = datetime.now().strftime("%H:%M:%S")

    # Get IP addresses
    source_ip = packet[IP].src
    destination_ip = packet[IP].dst

    # Default values
    protocol = "Other"
    source_port = "-"
    destination_port = "-"

    # ---------------- Protocol Detection ----------------

    if TCP in packet:
        protocol = "TCP"
        source_port = packet[TCP].sport
        destination_port = packet[TCP].dport

    elif UDP in packet:
        protocol = "UDP"
        source_port = packet[UDP].sport
        destination_port = packet[UDP].dport

    elif ICMP in packet:
        protocol = "ICMP"

    # Count protocols
    protocol_count[protocol] += 1

    # ---------------- Display Packet ---------------------

    print(f"\n{'─' * 75}")
    print(f" Packet #{packet_count:<5}                         Time: {current_time}")
    print(f"{'─' * 75}")

    print(f"  Source IP        : {source_ip}")
    print(f"  Destination IP   : {destination_ip}")
    print(f"  Protocol         : {protocol}")
    print(f"  Source Port      : {source_port}")
    print(f"  Destination Port : {destination_port}")
    print(f"  Packet Size      : {packet_size} bytes")

    print(f"{'─' * 75}")


# -------------------- Final Summary -----------------------


def display_summary():
    print("\n")
    print("=" * 75)
    print("                       CAPTURE SUMMARY")
    print("=" * 75)

    print(f"  Total Packets Captured : {packet_count}")
    print(f"  Total Data Captured    : {total_bytes} bytes")

    if packet_count > 0:
        average_size = total_bytes / packet_count
        print(f"  Average Packet Size    : {average_size:.2f} bytes")
    else:
        print("  Average Packet Size    : 0 bytes")

    print()
    print("  Protocol Statistics")
    print("  " + "-" * 30)

    if protocol_count:
        for protocol, count in protocol_count.items():
            percentage = (count / packet_count) * 100

            print(f"  {protocol:<10} : {count:<5} packets ({percentage:.1f}%)")

    else:
        print("  No IP packets were captured.")

    print("=" * 75)
    print("                 ANALYSIS COMPLETED")
    print("=" * 75)
    print()


# -------------------- Main Program ------------------------


def main():

    display_header()

    print("  Starting packet capture...")
    print("  Generate network traffic by browsing websites.")
    print()
    print("  Examples:")
    print("  • Open Google")
    print("  • Open YouTube")
    print("  • Search something")
    print("  • Refresh a webpage")
    print()
    print("  Press Ctrl+C to stop the capture.")
    print()
    print("=" * 75)

    try:
        # Capture packets continuously
        sniff(prn=analyze_packet, store=False)

    except KeyboardInterrupt:
        print("\n\n  Packet capture stopped by user.")

    except PermissionError:
        print("\n")
        print("=" * 75)
        print("  ERROR: Permission denied")
        print("=" * 75)
        print("  Packet capture requires appropriate permissions.")
        print("  Please run the program with the required permissions.")
        print("=" * 75)

    except Exception as error:
        print("\n")
        print("=" * 75)
        print("  ERROR OCCURRED")
        print("=" * 75)
        print(f"  {error}")
        print("=" * 75)

    finally:
        display_summary()


# -------------------- Program Start -----------------------

if __name__ == "__main__":
    main()
