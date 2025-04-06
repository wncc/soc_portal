import React from 'react';
import './textstyle.css';
import './scrollable.css';

export default function Textform(){
  return(
    <>
      <div >
        <h2 className="forSOC">
                What is SOC?
        </h2>
        <p className ="text" >
                SOC is one of the flagship events organised by WnCC, IIT Bombay. In this event a number of project are provided
                to the students and they have to apply for the project according to their interest. if selected they are provided
                mentors who are expert in their respective fields and help the students complete their project.
        </p>
      </div>
      <div>
        <h2>
                Past Year Stats
        </h2>
      </div>
      <div className="containerscrollable">
        <div className="container1" />
        <div className="container1" />
        <div className="container1" />
        <div className="container1" />
        <div className="container1" />
        <div className="container1" />
        <div className="container1" />
        <div className="container1" />
        <div className="container1" />
      </div>
      <div>
        <h2>
                Reviews
        </h2>
      </div>
    </>
  );
}
