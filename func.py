import connect # database
import sys
from dfply import *  # dplyr package for python
from functools import reduce

def overallStatusParser(query):

    try:
        result = connect.query(query)
    except:
        print('Problem with Zproc Connection (OverallStatus)')
        sys.exit(1)

    # Alias "energy" doesnt include the device name next to it. Which means all the Smart Switch aliases are labeled as Energy.
    energy = result[result.alias == "Energy"]

    # I wanted to use group_by location_id as well. But there are some devices that installed in different houses at
    # different points of time... Read the explanation
    # so for example a device x was installed in #008, for some reason it was removed and no other device was installed
    # for the location then we install device x into #010. So device x will be seen under two houses.
    # If I do group_by(location_id, alias)- these duplicated values won't be removed from the dataset
    # To avoid this, I should separate system status and disk status rows from the data set
    # and do all the data wrangling operations separately then merge all 3 data sets (energy, disk usage&status, Battery) together.

    diskAndSystem = result[(result.alias == "Disk Usage") | (result.alias == "System Status")]

    # For the rest of the alias. Basically batteries...
    filterList = ['Energy', 'Disk Usage', 'System Status']

    restAlias = result[~result.alias.isin(filterList)]

    restAlias = (restAlias >>
                 group_by(X.alias) >>
                 filter_by(X.last_processed_event_time == colmax(X.last_processed_event_time)) >>
                 ungroup())

    ###Check if restAlias works correctly
    # a = restAlias >> group_by(X.devid) >> summarize(c = n(X.alias))
    # b = restAlias >> group_by(X.devid) >> summarize(c = n_distinct(X.alias))
    # mergedAB = pd.merge(a, b, on=['devid'], how='inner')
    # 1 device appears in the list two times with two different alias name
    # mergedAB >> filter_by(X.c_x != 1) #there are two
    # mergedAB >> filter_by(X.c_y != 1)

    # Filter smartswitches based on last_processed_event_time
    energy = (energy >>
              group_by(X.devid) >>
              filter_by(X.last_processed_event_time == colmax(X.last_processed_event_time)) >>
              ungroup())

    # I can filter the dataset either based on the last_processed_event_time or the highest sensor ID. Used sensor ID
    diskAndSystem = (diskAndSystem >>
                     group_by(X.devid, X.alias) >>
                     filter_by(X.id == colmax(X.id)) >>
                     ungroup())

    # combine the datasets
    finalized = restAlias.append([energy, diskAndSystem], ignore_index=True)

    finalized = finalized.sort_values(by=['location_id'])

    ######
    overallStatus = (finalized >>
                     select(X.location_id, X.alias, X.devid, X.value, X.last_processed_event_time, X.event_time))

    # Convert value from object to in

    houseIDs = overallStatus.location_id.unique()

    # Overall System Status variables

    # systemStatus = overallStatus[(overallStatus.location_id == houseId) & (overallStatus.alias == 'System Status')]['value'].iloc[0]

    systemStatus = (overallStatus >> group_by(X.location_id) >> filter_by(X.alias == "System Status") >>
                    select(X.location_id, X.alias, X.value))

    diskUsage = (overallStatus >> group_by(X.location_id) >> filter_by(X.alias == "Disk Usage") >>
                 select(X.location_id, X.value))

    diskUsage = diskUsage.rename(columns={'value': 'SdCardUsage'})

    # recentEvent = overallStatus[(overallStatus.location_id == houseId)]['last_processed_event_time'].max().strftime("%Y-%m-%d %H:%M:%S")

    ### Why do we need total devices? So this variable is not being used...
    totalDevices = (overallStatus >> group_by(X.location_id) >> summarize(totalDevices=n_distinct(X.devid)))

    ### We can't really do working devices because we don't have periodic reporting for each sensor...So this variable is not being used...
    # add logging if this is empty so there is no event reported in the past 25 hours.....
    workingDevices = (overallStatus >> group_by(X.location_id) >>
                      filter_by(X.last_processed_event_time > (pd.Timestamp.now() - pd.Timedelta(hours=25))) >>
                      summarize(devidWorking=n_distinct(X.devid)))

    ###########
    # Sensor Health for MUlti and Zipato. Only Two of them reports periodic battery levels
    # set to 8 mins. It should report every 4 minutes
    sensorHealthMulti = (overallStatus >> group_by(X.location_id) >>
                         filter_by(X.alias.str.contains("USF.AL.MS")) >>
                         filter_by(X.last_processed_event_time < (pd.Timestamp.now() - pd.Timedelta(minutes=10))))

    # set to 70 minutes. it should report every 60 min
    sensorHealthZip = (overallStatus >> group_by(X.location_id) >>
                       filter_by(X.alias.str.contains("USF.ZP.MS")) >>
                       filter_by(X.last_processed_event_time < (pd.Timestamp.now() - pd.Timedelta(minutes=99))))

    # set to 20 minutes. it should report every 10 min
    sensorHealthSs = (overallStatus >> group_by(X.location_id) >>
                      filter_by(X.alias.str.contains("Energy")) >>
                      filter_by(X.last_processed_event_time < (pd.Timestamp.now() - pd.Timedelta(minutes=20))))

    # Row bind multi and zip
    sensorHealth = sensorHealthMulti.append(sensorHealthZip)
    sensorHealth = sensorHealth.append(sensorHealthSs)

    ### This for # of devices batteryLevel is low. Again, Why? we can display min Battery and highlight the ones have
    # low battery in HouseStatus.
    # batteryLevel = (overallStatus >> group_by(X.location_id) >>
    #               filter_by(X.alias.str.contains("Battery")) >>
    #              filter_by(X.value.astype(str).astype(int) < 25) >>
    #             summarize(devidBatteryLow=n_distinct(X.devid)))

    # Min battery for overallStatus table. Datatype is critical when it comes to min max values!
    minBattery = (overallStatus >> group_by(X.location_id) >>
                  filter_by(X.alias.str.contains("Battery")) >>
                  summarize(MinBattery=colmin(X.value.astype(str).astype(int))) >>
                  ungroup())
    # Last_process_time and last event time for any sensor
    lastZproc = (overallStatus >> group_by(X.location_id) >>
                 summarize(LastZprocEvent=colmax(X.last_processed_event_time)) >>
                 ungroup())
    lastZray = (overallStatus >> group_by(X.location_id) >>
                summarize(LastZrayEvent=colmax(X.event_time)) >>
                ungroup())

    # list of data frames
    dataFrames = [systemStatus, diskUsage, minBattery, lastZproc, lastZray]

    # merge dataframes based on location_id's
    finalOverall = reduce(lambda left, right: pd.merge(left, right, on=['location_id'], how='outer'),
                          dataFrames).fillna(
        'NA')

    # Add sensor health col
    indexes = np.in1d(finalOverall['location_id'], sensorHealth['location_id'])

    # Device Connectivity represents sensorHealth. Name has changed after development
    finalOverall['DeviceConnectivity'] = np.where(indexes == False, 'Yes', 'No')
    finalOverall.head()

    # X min ago
    xMinAgo = pd.Timestamp.now() - finalOverall.LastZprocEvent
    finalOverall["XminAgo"] = xMinAgo.astype('<m8[m]').astype(int)

    overallStatusFinal = finalOverall.to_dict('records')

    return overallStatusFinal

def houseStatusParser(query):

    try:
        result = connect.query(query)
    except:
        print('Problem with Zproc Connection (HouseStatus)')
        sys.exit(1)
        # Alias "energy" doesnt include the device name next to it. Which means all the Smart Switch aliases are labeled as Energy.
    energy = result[result.alias == "Energy"]

    # I wanted to use group_by location_id as well. But there are some devices that installed in different houses at
    # different points of time... Read the explanation so for example a device x was installed in #008, for some reason
    # it was removed and no other device was installed for the location
    # then we install device x into #010. So device x will be seen under two houses. If I do group_by(location_id, alias)
    # - these duplicated values won't be removed from the dataset
    # To avoid this, I should separate system status and disk status rows from the data set
    # and do all the data wrangling operations separately then merge all 3 data sets (energy, disk usage&status, Battery) together.

    diskAndSystem = result[(result.alias == "Disk Usage") | (result.alias == "System Status")]

    # For the rest of the alias. Basically batteries...
    filterList = ['Energy', 'Disk Usage', 'System Status']

    restAlias = result[~result.alias.isin(filterList)]

    restAlias = (restAlias >>
                 group_by(X.alias) >>
                 filter_by(X.last_processed_event_time == colmax(X.last_processed_event_time)) >>
                 ungroup())

    ###Check if restAlias works correctly
    # a = restAlias >> group_by(X.devid) >> summarize(c = n(X.alias))
    # b = restAlias >> group_by(X.devid) >> summarize(c = n_distinct(X.alias))
    # mergedAB = pd.merge(a, b, on=['devid'], how='inner')
    # 1 device appears in the list two times with two different alias name
    # mergedAB >> filter_by(X.c_x != 1) #there are two
    # mergedAB >> filter_by(X.c_y != 1)

    # Filter smartswitches based on last_processed_event_time
    energy = (energy >>
              group_by(X.devid) >>
              filter_by(X.last_processed_event_time == colmax(X.last_processed_event_time)) >>
              ungroup())

    # I can filter the dataset either based on the last_processed_event_time or the highest sensor ID. Does it matter which one?
    diskAndSystem = (diskAndSystem >>
                     group_by(X.devid, X.alias) >>
                     filter_by(X.id == colmax(X.id)) >>
                     ungroup())

    # combine the datasets
    finalized = restAlias.append([energy, diskAndSystem], ignore_index=True)

    finalized = finalized.sort_values(by=['location_id'])

    ######
    overallStatus = (finalized >>
                     select(X.location_id, X.alias, X.devid, X.value, X.last_processed_event_time, X.event_time))

    # Convert value from object to in

    houseIDs = overallStatus.location_id.unique()

    # Overall System Status variables

    # systemStatus = overallStatus[(overallStatus.location_id == houseId) & (overallStatus.alias == 'System Status')]['value'].iloc[0]

    systemStatus = (overallStatus >> group_by(X.location_id) >> filter_by(X.alias == "System Status") >>
                    select(X.location_id, X.alias, X.value))

    diskUsage = (overallStatus >> group_by(X.location_id) >> filter_by(X.alias == "Disk Usage") >>
                 select(X.location_id, X.value))

    diskUsage = diskUsage.rename(columns={'value': 'SdCardUsage'})

    # recentEvent = overallStatus[(overallStatus.location_id == houseId)]['last_processed_event_time'].max().strftime("%Y-%m-%d %H:%M:%S")

    ### Why do we need total devices? So this variable is not being used...
    totalDevices = (overallStatus >> group_by(X.location_id) >> summarize(totalDevices=n_distinct(X.devid)))

    ### We can't really do working devices because we don't have periodic reporting for each sensor...So this variable is not being used...
    # add logging if this is empty so there is no event reported in the past 25 hours.....
    workingDevices = (overallStatus >> group_by(X.location_id) >>
                      filter_by(X.last_processed_event_time > (pd.Timestamp.now() - pd.Timedelta(hours=25))) >>
                      summarize(devidWorking=n_distinct(X.devid)))

    ###########
    # Sensor Health for MUlti and Zipato. Only Two of them reports periodic battery levels
    # set to 8 mins. It should report every 4 minutes
    sensorHealthMulti = (overallStatus >> group_by(X.location_id) >>
                         filter_by(X.alias.str.contains("USF.AL.MS")) >>
                         filter_by(X.last_processed_event_time < (pd.Timestamp.now() - pd.Timedelta(minutes=10))))

    # set to 70 minutes. it should report every 60 min
    sensorHealthZip = (overallStatus >> group_by(X.location_id) >>
                       filter_by(X.alias.str.contains("USF.ZP.MS")) >>
                       filter_by(X.last_processed_event_time < (pd.Timestamp.now() - pd.Timedelta(minutes=99))))

    # Row bind multi and zip
    sensorHealth = sensorHealthMulti.append(sensorHealthZip)

    ### This for # of devices batteryLevel is low. Again, Why? we can display min Battery and highlight the ones have low battery in HouseStatus.
    # batteryLevel = (overallStatus >> group_by(X.location_id) >>
    #               filter_by(X.alias.str.contains("Battery")) >>
    #            filter_by(X.value.astype(str).astype(int) < 25) >>
    #        summarize(devidBatteryLow=n_distinct(X.devid)))
    # Min battery for overallStatus table. Datatype is critical when it comes to min max values!

    minBattery = (overallStatus >> group_by(X.location_id) >>
                  filter_by(X.alias.str.contains("Battery")) >>
                  summarize(MinBattery=colmin(X.value.astype(str).astype(int))) >>
                  ungroup())

    # Last_process_time and last event time for any sensor
    lastZproc = (overallStatus >> group_by(X.location_id) >>
                 summarize(LastZprocEvent=colmax(X.last_processed_event_time)) >>
                 ungroup())
    lastZray = (overallStatus >> group_by(X.location_id) >>
                summarize(LastZrayEvent=colmax(X.event_time)) >>
                ungroup())

    # list of data frames
    dataFrames = [systemStatus, diskUsage, minBattery, lastZproc, lastZray]

    # merge dataframes based on location_id's
    finalOverall = reduce(lambda left, right: pd.merge(left, right, on=['location_id'], how='outer'),
                          dataFrames).fillna(
        'NA')

    # Add sensor health col

    indexes = np.in1d(finalOverall['location_id'], sensorHealth['location_id'])

    # Device Connectivity represents sensorHealth
    finalOverall['DeviceConnectivity'] = np.where(indexes == False, 'Yes', 'No')

    ###HOUSE STATUS
    houseStatus = (finalized >> group_by(X.location_id))

    # Delete dev ids from alias
    def removeDevIds(string):
        if "-" in string:
            return string.split('-')[1].strip()
        else:
            return string

    houseStatus.alias = houseStatus.alias.apply(removeDevIds)

    # Sort by alias
    houseStatus = houseStatus.sort_values(by='devid')

    houseStatus = houseStatus.to_dict('records')

    return houseStatus