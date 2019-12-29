

function addButtonToTable(rowLength) {

    const grepCards = document.querySelectorAll(".eachHouse");

    for (let i = 0; i < rowLength; i++) {
        grepCards[i].addEventListener("click", function () {
            let houseForm = document.getElementById("houseForm");
            console.log(houseForm);
            let houseNumber = document.createElement("input");
            console.log(houseNumber);
            houseForm.appendChild(houseNumber);
            houseNumber.setAttribute("type", "hidden");
            houseNumber.setAttribute("name", "houseNumber");
            const locationId = document.querySelectorAll(".eachHouse .houseHeader .locationId")[i]
                .textContent;
            houseNumber.setAttribute("value", locationId);
            houseForm.submit()

        })
    }

}

const logicOverallStatus = (rowLength) => {
    //Grep em element which represent the variables: Min Battery, etc.
    const getHouse = document.querySelector(".eachHouse");
    const varNames = getHouse.querySelectorAll("em");

    //Convert nodelist to array -> map to get var names
    const varNamesArrTag = Array.from(varNames);
    const varNamesArr = varNamesArrTag.map(value => value.textContent);

    //Current Time
    const now = moment().format("YYYY-MM-DD HH:mm:ss");

    // Duration to check
    const systemDuration = moment.duration("00:60:00");

    //Threshold for last Process Event (Zproc)
    const thresholdSystem = moment(now).subtract(systemDuration).format("YYYY-MM-DD HH:mm:ss");

    //grep all cards
    const grepCards = document.querySelectorAll(".eachHouse");

    //Battery Level
    const batteryLevels = document.querySelectorAll(".eachHouse p .battery");
    for (let i = 0; i < rowLength; i++) {
        if (batteryLevels[i].textContent < 25) {
            grepCards[i].classList.add("lowBattery");
        }
    }

    //Sd Card Level
    const sdCardLevels = document.querySelectorAll(".eachHouse p .sdCard");
    for (let i = 0; i < rowLength; i++) {
        if (sdCardLevels[i].textContent > 85 || sdCardLevels[i].textContent == "NA") {
            grepCards[i].classList.add("highSdCard");
        }
    }

    //System Status
    const systemStatus = document.querySelectorAll(".eachHouse p .systemStat");
    for (let i = 0; i < rowLength; i++) {
        if (systemStatus[i].textContent != 10) {
            grepCards[i].classList.add("systemStatus");
        }
    }

    //Device Connectivity
    const devCon = document.querySelectorAll(".eachHouse p .deviceCon");
    for (let i = 0; i < rowLength; i++) {
        if (devCon[i].textContent != "Yes") {
            grepCards[i].classList.add("deviceConnectivity");
        }
    }

    //Last Processed Zproc
    const eventZproc = document.querySelectorAll(".eachHouse p .eventZproc");
    for (let i = 0; i < rowLength; i++) {
        //grep and convert reported date and time
        let dateTimeSystem = moment(eventZproc[i].textContent).format("YYYY-MM-DD HH:mm:ss");

        if (moment(thresholdSystem).isAfter(dateTimeSystem)) {
            grepCards[i].classList.add("lastProcessedZproc");
        }
    }
}


const logicHouseStatus = () => {
    //create colIndexes in case you add/remove a col.
    const colNames = document.querySelectorAll("#HouseStatusTable tr th")
    const colNamesArrTag = Array.from(colNames);

    const colNamesArr = colNamesArrTag.map(value => value.textContent);
    const indexModel = colNamesArr.indexOf("Model");
    const indexValue = colNamesArr.indexOf("Value");
    const indexAlias = colNamesArr.indexOf("Alias");
    //const indexEventTime = colNamesArr.indexOf("Event Time"); Event time comes from Zray


    const tableHouse = document.querySelector("#HouseStatusTable");
    const rowLengthHouse = document.querySelector("#HouseStatusTable").rows.length - 1;


    for (let i = 1; i < rowLengthHouse + 1; i++) {
        //Battery Level for specific device
        for (let j = indexValue; j < indexValue + 1; j++) {
            if (tableHouse.rows[i].cells[j].textContent < 25 && tableHouse.rows[i].cells[indexAlias].
                textContent.includes("Battery")) {
                tableHouse.rows[i].classList.add("lowBattery")
            }
        }

        //Sd Card Level
        for (let j = indexAlias; j < indexAlias + 1; j++) {
            if (tableHouse.rows[i].cells[j].textContent.includes("Disk Usage") && tableHouse.rows[i].cells[indexValue].
                textContent > 85) {
                tableHouse.rows[i].classList.add("highSdCard")
            }
        }
        //System Status
        for (let j = indexAlias; j < indexAlias + 1; j++) {
            if (tableHouse.rows[i].cells[j].textContent.includes("System Status") && tableHouse.rows[i].cells[indexValue].
                textContent != 10) {
                tableHouse.rows[i].classList.add("systemStatus")
            }
        }

    }
}

// This function can be utilized.
const logicSensorHealth = () => {

    const colNames = document.querySelectorAll("#HouseStatusTable tr th")
    const colNamesArrTag = Array.from(colNames);
    const colNamesArr = colNamesArrTag.map(value => value.textContent);
    const indexDevId = colNamesArr.indexOf("Dev Id");
    const indexLastProcessed = colNamesArr.indexOf("Event Time (Zproc)");

    const tableHouse = document.querySelector("#HouseStatusTable");
    const rowLengthHouse = document.querySelector("#HouseStatusTable").rows.length - 1;
    //Time comparison & threshold values for Zipato and Multisensor
    const now = moment().format("YYYY-MM-DD HH:mm:ss");
    //Durations for each device type
    const zpDuration = moment.duration("00:99:00"); //99 mins
    const multiDuration = moment.duration("00:10:00");
    const ssDuration = moment.duration("00:20:00");
    const thresholdZP = moment(now).subtract(zpDuration).format("YYYY-MM-DD HH:mm:ss");
    const thresholdMulti = moment(now).subtract(multiDuration).format("YYYY-MM-DD HH:mm:ss");
    const thresholdSs = moment(now).subtract(ssDuration).format("YYYY-MM-DD HH:mm:ss");

    for (let i = 1; i < rowLengthHouse + 1; i++) {
        //Sensor Health of Zipato
        for (let j = indexDevId; j < indexDevId + 1; j++) {
            if (tableHouse.rows[i].cells[j].textContent.includes(".ZP.")) {
                let dateTime = moment(tableHouse.rows[i].cells[indexLastProcessed].textContent).format("YYYY-MM-DD HH:mm:ss");
                if (moment(thresholdZP).isAfter(dateTime)) {
                    tableHouse.rows[i].classList.add("deviceConnectivity")

                }
            }
        }

        for (let j = indexDevId; j < indexDevId + 1; j++) {
            if (tableHouse.rows[i].cells[j].textContent.includes(".AL.MS.")) {
                let dateTimeMulti = moment(tableHouse.rows[i].cells[indexLastProcessed].textContent).format("YYYY-MM-DD HH:mm:ss");
                if (moment(thresholdMulti).isAfter(dateTimeMulti)) {
                    tableHouse.rows[i].classList.add("deviceConnectivity")

                }
            }
        }

        for (let j = indexDevId; j < indexDevId + 1; j++) {
            if (tableHouse.rows[i].cells[j].textContent.includes(".AL.SS.")) {
                let dateTimeSs = moment(tableHouse.rows[i].cells[indexLastProcessed].textContent).format("YYYY-MM-DD HH:mm:ss");
                if (moment(thresholdSs).isAfter(dateTimeSs)) {
                    tableHouse.rows[i].classList.add("deviceConnectivity")

                }
            }
        }

    }
}

const search = () => {
    let input = document.querySelector('#searchBar')
    let filter = input.value.toUpperCase();
    let table = document.querySelector('#HouseStatusTable');
    let tr = table.getElementsByTagName("tr");
    let found;
    for (i = 1; i < tr.length; i++) {
        let td = tr[i].getElementsByTagName("td");
        for (j = 0; j < td.length; j++) {
            if (td[j].innerHTML.toUpperCase().indexOf(filter) > -1) {
                found = true;
            }
        }
        if (found) {
            tr[i].style.display = "";
            found = false;
        } else {
            tr[i].style.display = "none";
        }
    }
}





