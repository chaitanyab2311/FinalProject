import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch } from '@fortawesome/free-solid-svg-icons';
import './App.css';
import { Dimmer, Loader } from 'semantic-ui-react'

const SearchBar = () => {

    const [showTable, setshowTable] = useState(false);
    const [amazonData, setAmazonData] = useState([]);
    const [ebayData, setEbayData] = useState([]);
    const [bestbuyData, setBestbuyData] = useState([]);
    const [showLoader, setLoader] = useState(false);
    const [mostSearched, setMostSearched] = useState({});

    const url = "http://localhost:5000/apiv1/fetchPrices";
    const mostsearchedurl = "http://localhost:5000/apiv1/getMostSearched";

    useEffect(() => {
        setLoader(true);
        axios.post(`${mostsearchedurl}`)
            .then((response) => {
                setLoader(false);
                setMostSearched(response.data);
            })
            .catch((error) => {
                console.log("Error occured in most searched api", error);
                console.error('Error: ${error}');
            }
            );
    }, []);


    let name = '';

    function read(e) {
        name = e.target.value;
    }

    function search(e) {
        e.preventDefault();
        setLoader(true);
        axios.post(`${url}`, { product_name: name })
            .then((response) => {
                console.log(response)
                console.log(response)
                setshowTable(true);
                setLoader(false);
                setAmazonData(response.data.amazon);
                setEbayData(response.data.ebay);
                setBestbuyData(response.data.bestbuy);
                

                axios.post(`${mostsearchedurl}`)
                    .then((response) => {
                        setLoader(false);
                        setMostSearched(response.data);
                    })
                    .catch((error) => {
                        console.log("Error occured in most searched api", error);
                        console.error('Error: ${error}');
                    }
                    );


            })
            .catch((error) => {
                console.log("Error occured in fetch prices api", error);
                console.error('Error: ${error}');
            }
            );

    }

    return (
        <div>
            <div style={{ display: 'flex' }}>
                <div style={{ width: '70%' }}>

                    {showLoader ? (
                        <div>
                            <Dimmer active><Loader /></Dimmer>
                        </div>) : null
                    }

                    <div className="wrap">
                        <div className="search">
                            <label htmlFor="header-search">
                                <span className="visually-hidden"></span>
                            </label>


                            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
                                <input
                                    type="text"
                                    id="header-search"
                                    onChange={read}
                                    className="button"
                                    placeholder="Search for items"
                                    name="s"

                                />

                                <button type="submit" className="searchButton" onClick={search} >Search
                                    <FontAwesomeIcon icon={faSearch} />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                <div style={{ width: '30%', margin: '5px' }}>
                    <h3 style={{ textAlign: 'center' }}>Most searched Products (Top 5)</h3>



                    <table className="styled-table">
                        <thead className="cellcontainer">

                            <tr>
                                <th>Product Name</th>
                                <th>Searched times</th>

                            </tr>


                        </thead>
                        <tbody className="cellcontainer">

                            {Object.keys(mostSearched).map((key, index) => {
                                return (
                                    <tr key={index}>
                                        <td>
                                            {key}
                                        </td>
                                        <td>
                                            {mostSearched[key]}
                                        </td>
                                    </tr>
                                );
                            })
                            }

                        </tbody>
                    </table>


                </div>
            </div>
            {showTable == true ? (
                <div className="container">
                    <div style={{ display: 'flex', justifyContent: 'center', height: '-25vh' }}>

                        <div style={{ width: '33%' }}>

                            <h3 style={{ textAlign: 'center' }}>Amazon</h3>

                            <table className="styled-table">


                                <thead className="cellcontainer">
                                    <tr>
                                        <th>Product Name</th>
                                        <th>Product Price</th>
                                    </tr>

                                </thead>
                                <tbody className="cellcontainer">


                                    {amazonData.map((listValue, index) => {
                                        return (

                                            <tr key={index} style={{ backgroundColor: index == 0 ? '#dfd' : "#ffffff" }}>
                                                <td>
                                                    <img src={listValue.product_image_url}></img>
                                                </td>
                                                <td>
                                                    <a href={'http://www.amazon.com/' + listValue.product_url}>
                                                        {listValue.productname}
                                                    </a>
                                                    <div><b>${listValue.productprice}</b></div>
                                                </td>
                                            </tr>
                                        );
                                    })}

                                </tbody>
                            </table>
                        </div>

                        <div style={{ width: '33%' }}>

                            <h3 style={{ textAlign: 'center' }}>Ebay</h3>

                            <table className="styled-table">
                                <thead className="cellcontainer">

                                    <tr>
                                        <th>Product Name</th>
                                        <th>Product Price</th>

                                    </tr>


                                </thead>
                                <tbody className="cellcontainer">


                                    {ebayData.map((listValue, index) => {
                                        return (

                                            <tr key={index} style={{ backgroundColor: index == 0 ? '#dfd' : "#ffffff" }}>
                                                <td>
                                                    <img src={listValue.product_image_url}></img>
                                                </td>
                                                <td>
                                                    <a href={listValue.product_url}>
                                                        {listValue.productname}
                                                    </a>
                                                    <div><b>${listValue.productprice}</b></div>
                                                </td>
                                            </tr>
                                        );
                                    })}

                                </tbody>
                            </table>
                        </div>

                        <div style={{ width: '33%' }}>

                            <h3 style={{ textAlign: 'center' }}>BestBuy</h3>

                            <table className="styled-table">
                                <thead className="cellcontainer">

                                    <tr>
                                        <th>Product Name</th>
                                        <th>Product Price</th>

                                    </tr>


                                </thead>
                                <tbody className="cellcontainer">


                                    {bestbuyData.map((listValue, index) => {
                                        return (

                                            <tr key={index} style={{ backgroundColor: index == 0 ? '#dfd' : "#ffffff" }}>
                                                <td>
                                                    <img src={listValue.product_image_url}></img>
                                                </td>
                                                <td>
                                                    <a href={ 'http://www.bestbuy.com/' + listValue.product_url}>
                                                        {listValue.productname}
                                                    </a>
                                                    <div><b>${listValue.productprice}</b></div>
                                                </td>
                                            </tr>
                                        );
                                    })}

                                </tbody>
                            </table>
                        </div>
                        

                    </div>
                </div>

            ) : (<div style={{ textAlign: 'center' }}>No data present</div>)
            }
        </div>
    );

}

export default SearchBar;
