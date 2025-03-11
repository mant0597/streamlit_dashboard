import streamlit as st
from datetime import datetime
import time
from pyzbar.pyzbar import decode
from PIL import Image
import cv2
import numpy as np

def showBrandLogo():
    st.image("https://via.placeholder.com/150x50.png?text=Your+Logo", width=150)

def addSpacing(n):
    for _ in range(n):
        st.write("")

def processQRCode():
    uploaded_image = st.file_uploader("Upload the QR Code Image", type=["png", "jpg", "jpeg"])
    if uploaded_image is not None:
        img = Image.open(uploaded_image)
        decoded_data = decode(img)
        if decoded_data:
            return decoded_data[0].data.decode("utf-8")
        else:
            st.error("No QR code detected in the image.")
    return None

def initializeState():
    if "clientsList" not in st.session_state:
        st.session_state.clientsList = ["Manthan", "Wilson", "Mark"]

    if "statusMessage" not in st.session_state:
        st.session_state.statusMessage = "Shipment Process Started"

    if "selectedClient" not in st.session_state:
        st.session_state.selectedClient = ''

    if "shipmentIdentifier" not in st.session_state:
        st.session_state.shipmentIdentifier = False

    if "boxCount" not in st.session_state:
        st.session_state.boxCount = 0

    if "batchId" not in st.session_state:
        st.session_state.batchId = False

    if "currentBoxIndex" not in st.session_state:
        st.session_state.currentBoxIndex = 0

    if "currentItemIndex" not in st.session_state:
        st.session_state.currentItemIndex = 1

    if "boxStatus" not in st.session_state:
        st.session_state.boxStatus = []

    if "itemsCount" not in st.session_state:
        st.session_state.itemsCount = []

    if "shipmentDetails" not in st.session_state:
        st.session_state.shipmentDetails = []

    if "scanningMode" not in st.session_state:
        st.session_state.scanningMode = 'SingleItem' 

    if "bulkProcess" not in st.session_state:
        st.session_state.bulkProcess = False

def beginShipment(user):
    showBrandLogo()
    addSpacing(4)
    st.write(f"Greetings, :red[{user}]!")
    st.subheader("Initiate Shipment Processing")
    st.write("")

    if st.button("Start Shipment", key="initiateShipment"):
        st.session_state.statusMessage = "Started"
        st.rerun()

def processShipment(user):
    showBrandLogo()
    addSpacing(4)
    st.write(f"Hello, :red[{user}]!")
    addSpacing(1)

    col1, col2, col3 = st.columns([0.2, 1, 0.2])
    with col2:
        selectClient()

        if st.session_state.selectedClient:
            st.subheader(f"{st.session_state.statusMessage} for {st.session_state.selectedClient} :")
            st.write("")

            if not st.session_state.shipmentIdentifier:
                enterShipmentCode()
                if st.session_state.shipmentIdentifier:
                    st.rerun()
            else:
                st.write(f"*Shipment ID :* {st.session_state.shipmentIdentifier}")

                defineBoxCount()

                if st.session_state.boxCount != 0:
                    st.write(f"*Boxes in Shipment :* {st.session_state.boxCount}")
                    addSpacing(2)

                    if not st.session_state.boxStatus:
                        st.session_state.boxStatus = [0] * st.session_state.boxCount
                        st.session_state.itemsCount = [0] * st.session_state.boxCount
                        st.session_state.shipmentDetails = [[] for _ in range(st.session_state.boxCount)]

                    findNextBox(st.session_state.boxStatus)

                    if st.session_state.currentBoxIndex is not None:
                        st.write(f":stopwatch: Scanning *Box : {st.session_state.currentBoxIndex + 1}*")

                        if st.session_state.boxStatus[st.session_state.currentBoxIndex] == 0 or \
                                st.session_state.boxStatus[st.session_state.currentBoxIndex] == 'InProgress':
                            if st.session_state.itemsCount[st.session_state.currentBoxIndex] == 0:
                                numberOfItems = st.number_input(
                                    f"*Enter total props (items) for Box {st.session_state.currentBoxIndex + 1}: ",
                                    key=f"numberOfItems{st.session_state.currentBoxIndex}", value=0, min_value=0)
                                st.session_state.itemsCount[st.session_state.currentBoxIndex] = numberOfItems
                                st.session_state.shipmentDetails[st.session_state.currentBoxIndex] = [""] * (numberOfItems + 1)
                                addSpacing(2)

                            if st.session_state.itemsCount[st.session_state.currentBoxIndex] != 0:
                                if st.session_state.shipmentDetails[st.session_state.currentBoxIndex][0] == "":
                                    scanBoxIdentifier()
                                    if st.session_state.shipmentDetails[st.session_state.currentBoxIndex][0] != "":
                                        st.rerun()
                                elif st.session_state.shipmentDetails[st.session_state.currentBoxIndex][0] != "":
                                    st.session_state.scanningMode = st.selectbox("Choose scan mode:", ["SingleItem", "BulkItems"],
                                                                                key="scanModeSelector", index=None)
                                    if st.session_state.scanningMode == 'SingleItem':
                                        singleItemScan(st.session_state.shipmentDetails, st.session_state.currentBoxIndex)
                                    else:
                                        bulkItemScan(st.session_state.shipmentDetails, st.session_state.currentBoxIndex)
                                    if all(p != "" for p in st.session_state.shipmentDetails[st.session_state.currentBoxIndex][1:]):
                                        st.session_state.boxStatus[st.session_state.currentBoxIndex] = 'Completed'
                                        st.toast(f"*Box {st.session_state.currentBoxIndex + 1} :white_check_mark:*")
                                        time.sleep(1)
                                        st.rerun()

                        if all(p != "" for p in st.session_state.shipmentDetails[st.session_state.currentBoxIndex][1:]):
                            addSpacing(2)
                            with st.expander("*View Shipment Details*"):
                                st.write(st.session_state.shipmentDetails)

                    else:
                        if st.session_state.statusMessage != ":green[Shipment Ready]":
                            st.session_state.statusMessage = ":green[Shipment Ready]"
                            st.rerun()
                        st.success('All Boxes Processed!')
                        with st.expander(":red[Shipment Data :]", expanded=True):
                            st.write(f"*Shipment ID :* {st.session_state.shipmentIdentifier}")
                            st.write(f"Shipment details: ", st.session_state.shipmentDetails)

def selectClient():
    if not st.session_state.selectedClient:
        st.session_state.selectedClient = st.selectbox("Choose a client :", st.session_state.clientsList,
                                                       placeholder="Click to select a client", key="clientSelection",
                                                       index=None)

def enterShipmentCode():
    shipmentCode = st.text_input(label="Enter shipment ID manually:", placeholder="example: NW/2025/MANT", key="manualShipmentCode")
    if shipmentCode:
        st.session_state.shipmentIdentifier = shipmentCode.replace("/", "-")
        st.success(f" :green[Update Successful], Shipment ID : {st.session_state.shipmentIdentifier}")

def defineBoxCount():
    if st.session_state.boxCount == 0:
        boxCount = st.number_input("Enter total *boxes* in the shipment:", key="totalBoxes", value=0, min_value=0)
        st.session_state.boxCount = boxCount

def findNextBox(status):
    if st.session_state.boxCount != 0:
        st.session_state.currentBoxIndex = getNextBoxIndex(status)

def getNextBoxIndex(data):
    for i in range(len(data)):
        if data[i] == 0 or data[i] == 'InProgress':
            return i
    return None

def scanBoxIdentifier():
    boxCode = st.text_input(f"Enter Box {st.session_state.currentBoxIndex + 1} identifier:", key=f"boxCode{st.session_state.currentBoxIndex}")
    if boxCode:
        st.session_state.shipmentDetails[st.session_state.currentBoxIndex][0] = boxCode
        st.session_state.boxStatus[st.session_state.currentBoxIndex] = 'InProgress'
        st.session_state.currentItemIndex = 1
        st.rerun()

def bulkItemScan(details, boxIndex):
    itemCodes = st.text_input(label="Enter all item codes (comma-separated):", key=f"itemsOf{st.session_state.currentBoxIndex}").split(',')
    if len(itemCodes) == st.session_state.itemsCount[st.session_state.currentBoxIndex]:
        if validateEntries(itemCodes):
            st.session_state.shipmentDetails[st.session_state.currentBoxIndex][1:] = itemCodes
            st.session_state.shipmentDetails[st.session_state.currentBoxIndex].append("Completed")
            st.session_state.boxStatus[st.session_state.currentBoxIndex] = 'Completed'
            moveToNextBox()
            st.rerun()
        else:
            st.error("Duplicate entries found, Please Try again!")
    else:
        st.error("Please enter the correct number of items.")

ip_webcam_url = "http://192.168.69.227:8080/video"  

def capture_qr_code_from_ip():
    """Capture a frame from IP webcam and detect QR code."""
    cap = cv2.VideoCapture(ip_webcam_url)  
    
    if not cap.isOpened():
        st.error("Error: Could not open video stream.")
        return None
    
    ret, frame = cap.read()
    if ret:
        decoded_objects = decode(frame)  
        
        if decoded_objects:
            qr_code_data = decoded_objects[0].data.decode("utf-8")
            cap.release() 
            return qr_code_data
        else:
            cap.release()
            return None
    else:
        cap.release()
        return None

def singleItemScan(details, boxIndex):
    st.write(f"Enter code for Item {st.session_state.currentItemIndex}:")

    upload_choice = st.radio("Select how you want to capture the item code:", ("Upload QR Code", "Scan QR Code", "Enter Manually"))

    if upload_choice == "Upload QR Code":
        uploaded_image = st.file_uploader("Upload QR Code Image", type=["png", "jpg", "jpeg"])
        if uploaded_image:
            img = Image.open(uploaded_image)
            decoded_data = decode(img)
            if decoded_data:
                qr_code_data = decoded_data[0].data.decode("utf-8")
                st.session_state.shipmentDetails[boxIndex][st.session_state.currentItemIndex] = qr_code_data
                st.text_input("Item Code:", value=qr_code_data, key=f"itemCode{st.session_state.currentItemIndex}")

                st.session_state.currentItemIndex += 1

                if st.session_state.currentItemIndex > st.session_state.itemsCount[boxIndex]:
                    st.session_state.shipmentDetails[boxIndex].append("Completed")
                    st.session_state.boxStatus[boxIndex] = 'Completed'
                    st.success(f"Box {boxIndex + 1} has been completed!")
                    moveToNextBox()
                else:
                    st.rerun()  

            else:
                st.error("No QR code detected in the image. You can enter the item code manually.")

    elif upload_choice == "Scan QR Code":
        if 'qr_code_scanned' not in st.session_state or not st.session_state.qr_code_scanned:
            qr_code_data = capture_qr_code_from_ip()
            if qr_code_data:

                st.session_state.shipmentDetails[boxIndex][st.session_state.currentItemIndex] = qr_code_data
                st.text_input("Item Code:", value=qr_code_data, key=f"itemCode{st.session_state.currentItemIndex}")

                st.session_state.qr_code_scanned = True

                st.session_state.currentItemIndex += 1

                if st.session_state.currentItemIndex > st.session_state.itemsCount[boxIndex]:
                    st.session_state.shipmentDetails[boxIndex].append("Completed")
                    st.session_state.boxStatus[boxIndex] = 'Completed'
                    st.success(f"Box {boxIndex + 1} has been completed!")
                    moveToNextBox()
                else:
                    st.rerun() 
            else:
                st.write("No QR code detected. Please try scanning again or enter manually.")
        else:
            st.warning("QR Code already scanned for this item. Move to the next item.")

    elif upload_choice == "Enter Manually":
        item_code = st.text_input(f"Enter the code for Item {st.session_state.currentItemIndex}:")
        if item_code:
            st.session_state.shipmentDetails[boxIndex][st.session_state.currentItemIndex] = item_code
            st.session_state.currentItemIndex += 1

            if st.session_state.currentItemIndex > st.session_state.itemsCount[boxIndex]:
                st.session_state.shipmentDetails[boxIndex].append("Completed")
                st.session_state.boxStatus[boxIndex] = 'Completed'
                st.success(f"Box {boxIndex + 1} has been completed!")
                moveToNextBox()
            else:
                st.rerun() 

def moveToNextBox():
    nextBoxIndex = getNextBoxIndex(st.session_state.boxStatus)
    if nextBoxIndex is not None:
        st.session_state.currentBoxIndex = nextBoxIndex
        st.session_state.currentItemIndex = 1
        st.session_state.scanningMode = 'SingleItem' 
        st.rerun()
    else:
        st.session_state.statusMessage = ":green[Shipment Ready]"
        st.success("All Boxes Processed!")
        with st.expander(":red[Shipment Data :]", expanded=True):
            st.write(f"*Shipment ID :* {st.session_state.shipmentIdentifier}")
            st.write(f"Shipment details: ", st.session_state.shipmentDetails)

def validateEntries(items):
    return len(items) == len(set(items))

def main():
    initializeState()
    username = "Admin"

    if "statusMessage" not in st.session_state or st.session_state.statusMessage == "NotStarted":
        beginShipment(username)
    else:
        processShipment(username)

if __name__ == "__main__":
    main()
