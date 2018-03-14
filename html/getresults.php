	<?php
	require("db.php");

	//error_reporting(E_ALL);
	//ini_set('display_errors', 1);

	function setSeries(&$results, $series)
	{
		foreach ($results as &$result)
		{
			if ($result['structure'] == $series['structure'] && $result['thermostat'] == $series['thermostat'])
			{
				$result=$series;
				return;
			}
		}

		$results[]=$series;
	}

	function findResult($results, $structure, $thermostat)
	{
		foreach ($results as $result)
		{
			if ($result['structure'] == $structure && $result['thermostat'] == $thermostat)
			{
				return $result;
			}
		}

		return array
		(
			'structure' => $structure,
			'thermostat' => $thermostat,
		);
	}

	$offset=0;

	if (isset($_GET["offset"]))
	{
		$offset=-$_GET["offset"];
	}

	$results = array();

	$db = new mysqli($DB_HOST, $DB_USER, $DB_PASSWORD);
	if (!$db->connect_error)
	{
		if ($db->select_db($DB_DB))
		{
			$query="select * from measurements where (timestamp >= DATE_ADD(CURRENT_DATE(), INTERVAL " . $db->real_escape_string($offset) . " day) AND timestamp <= DATE_ADD(CURRENT_DATE(), INTERVAL " . $db->real_escape_string($offset+1) . " day)) order by timestamp";

			if ($result = $db->query($query))
			{
				while ($row = $result->fetch_assoc())
				{
					$series = findResult($results, $row["structure_id"], $row["thermostat_id"]);

					switch ($row["hvacstate"])
					{
						case "eco":
							$hvacstate=0;
							break;

						case "cool":
							$hvacstate=1;
							break;

						case "off":
							$hvacstate=2;
							break;

						case "heating":
							$hvacstate=3;
							break;

						case "heat-cool":
							$hvacstate=4;
							break;
					}

					$timestamp=round(strtotime($row["timestamp"])/60)*60*1000;
					$series['targettemp']['data'][] = array($timestamp, $row["targettemp"]);
					$series['ambienttemp']['data'][] = array($timestamp, $row["ambienttemp"]);
					$series['humidity']['data'][] = array($timestamp, $row["humidity"]);
					$series['hvacstate']['data'][] = array($timestamp, $hvacstate);

					setSeries($results, $series);
				}

				echo json_encode($results, JSON_PRETTY_PRINT | JSON_NUMERIC_CHECK);
			}
			else
			{
				die("Error querying: " . $db->error);
			}
		}
		else
		{
			die("Error selecting db: " . $db->error);
		}
	}
	else
	{
		die("Error connecting: " . $db->connect_error);
	}

	?>
