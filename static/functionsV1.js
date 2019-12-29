

function addButtonToTable(rowLength) {
    let tableOverall = document.querySelector("#OverallStatusTable");

        for (let i=1; i < rowLength+1; i++) {
            for (let j=0; j < 1; j++) {
               tableOverall.rows[i].cells[j].addEventListener("click", function() {
                let houseForm = document.getElementById("houseForm");
                let houseNumber = document.createElement("input");
                houseForm.appendChild(houseNumber);
                houseNumber.setAttribute("type","hidden");
                houseNumber.setAttribute("name","houseNumber");
                houseNumber.setAttribute("value",this.textContent);
                houseForm.submit();
            })
        }
    }

}


const logicOverallStatus = (rowLength) => {
    const colNames = document.querySelectorAll("#OverallStatusTable tr th");
    const colNamesArrTag = Array.from(colNames);
    const colNamesArr = colNamesArrTag.map(value => value.textContent);
    //Save indexes in case of a new col is added.
    const indexBattery = colNamesArr.indexOf('Min Battery');
    const indexSdCard = colNamesArr.indexOf('Sd Card Usage');
    const systemStatus = colNamesArr.indexOf('System Status');
    const indexDeviceConnectivity = colNamesArr.indexOf('Device Connectivity');

    const indexLastProcessedZray = colNamesArr.indexOf("Last Process Event (Zray)");

    //Current Time
    const now = moment().format("YYYY-MM-DD HH:mm:ss");
    // Duration to check
    const systemDuration = moment.duration("00:60:00");
    //Threshold for last Process Event (Zray)
    const thresholdSystem = moment(now).subtract(systemDuration).format("YYYY-MM-DD HH:mm:ss");

    const tableOverall = document.querySelector("#OverallStatusTable")
    for (let i=1; i < rowLength+1; i++) {

            //Battery Level
        for (let j=indexBattery; j < indexBattery + 1; j++) {
            if(tableOverall.rows[i].cells[j].textContent < 25) {
               tableOverall.rows[i].classList.add("lowBattery")
            }
        }
            //Sd Card Level
        for (let j=indexSdCard; j < indexSdCard + 1; j++) {
            if(tableOverall.rows[i].cells[j].textContent > 85) {
               tableOverall.rows[i].classList.add("highSdCard")
            }
        }
            //System Status
        for (let j=systemStatus; j < systemStatus + 1; j++) {
            if(tableOverall.rows[i].cells[j].textContent != 10) {
               tableOverall.rows[i].classList.add("systemStatus")
             }
        }
           //Device Connectivity
        for (let j=indexDeviceConnectivity; j < indexDeviceConnectivity + 1; j++) {
            if(tableOverall.rows[i].cells[j].textContent != "Yes") {
               tableOverall.rows[i].classList.add("deviceConnectivity")
             }
        }
          //Last Processed Zray
        for (let j=indexLastProcessedZray; j < indexLastProcessedZray + 1; j++) {
            //Get the last time recorded for Zray
            let dateTimeSystem = moment(tableOverall.rows[i].cells[indexLastProcessedZray].textContent).format("YYYY-MM-DD HH:mm:ss");
            if(moment(thresholdSystem).isAfter(dateTimeSystem)) {
                tableOverall.rows[i].classList.add("lastProcessedZray")

              }

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
  const rowLengthHouse= document.querySelector("#HouseStatusTable").rows.length -1;


  for (let i=1; i < rowLengthHouse+1; i++) {
            //Battery Level for specific device
        for (let j=indexValue; j < indexValue + 1; j++) {
            if(tableHouse.rows[i].cells[j].textContent < 25 && tableHouse.rows[i].cells[indexAlias].
            textContent.includes("Battery")) {
              tableHouse.rows[i].classList.add("lowBattery")
            }
        }

            //Sd Card Level
        for (let j=indexAlias; j < indexAlias + 1; j++) {
            if(tableHouse.rows[i].cells[j].textContent.includes("Disk Usage") && tableHouse.rows[i].cells[indexValue].
            textContent > 75) {
               tableHouse.rows[i].classList.add("highSdCard")
            }
        }
            //System Status
        for (let j=indexAlias; j < indexAlias + 1; j++) {
            if(tableHouse.rows[i].cells[j].textContent.includes("System Status") && tableHouse.rows[i].cells[indexValue].
            textContent != 10 ) {
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
    const rowLengthHouse= document.querySelector("#HouseStatusTable").rows.length -1;
    //Time comparison & threshold values for Zipato and Multisensor
    const now = moment().format("YYYY-MM-DD HH:mm:ss");
    //Durations for each device type
    const zpDuration = moment.duration("00:99:00"); //99 mins
    const multiDuration = moment.duration("00:10:00");
    const ssDuration = moment.duration("00:20:00");
    const thresholdZP = moment(now).subtract(zpDuration).format("YYYY-MM-DD HH:mm:ss");
    const thresholdMulti = moment(now).subtract(multiDuration).format("YYYY-MM-DD HH:mm:ss");
    const thresholdSs = moment(now).subtract(ssDuration).format("YYYY-MM-DD HH:mm:ss");




    for (let i=1; i < rowLengthHouse+1; i++) {
            //Sensor Health of Zipato
        for (let j=indexDevId; j < indexDevId + 1; j++) {
            if(tableHouse.rows[i].cells[j].textContent.includes(".ZP.")) {
                let dateTime = moment(tableHouse.rows[i].cells[indexLastProcessed].textContent).format("YYYY-MM-DD HH:mm:ss");
                if(moment(thresholdZP).isAfter(dateTime)) {
                    tableHouse.rows[i].classList.add("deviceConnectivity")

                }
            }
        }

        for (let j=indexDevId; j < indexDevId + 1; j++) {
            if(tableHouse.rows[i].cells[j].textContent.includes(".AL.MS.")) {
                let dateTimeMulti = moment(tableHouse.rows[i].cells[indexLastProcessed].textContent).format("YYYY-MM-DD HH:mm:ss");
                if(moment(thresholdMulti).isAfter(dateTimeMulti)) {
                    tableHouse.rows[i].classList.add("deviceConnectivity")

                }
            }
        }

        for (let j=indexDevId; j < indexDevId + 1; j++) {
            if(tableHouse.rows[i].cells[j].textContent.includes(".AL.SS.")) {
                let dateTimeSs = moment(tableHouse.rows[i].cells[indexLastProcessed].textContent).format("YYYY-MM-DD HH:mm:ss");
                if(moment(thresholdSs).isAfter(dateTimeSs)) {
                    tableHouse.rows[i].classList.add("deviceConnectivity")

                }
            }
        }

    }
}

const search = () => {
    let input = document.querySelector('#searchBar')
    let filter = input.value.toUpperCase();
    let table  = document.querySelector('#HouseStatusTable');
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






