<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="/root" >
    <html >
        <head >
           <title >Movie List</title>
        </head >
        <body >
    	    <header >
                <h1 >List Of Movies</h1>
    	    </header>
            <table border="0" >
	            <thead >
	                <tr >
				        <th >Title</th>
				        <th >Date</th>
				        <th >Director(s)</th>
				        <th >Star(s)</th>
				        <th >Genre(s)</th>
	                </tr>
	            </thead>
	            <tbody >
                    <xsl:apply-templates mode="movieEntity">
                        <!-- depth used to keep track of recursion depth -->
                        <xsl:with-param name="depth" select="0"/>
                    </xsl:apply-templates>
	            </tbody>
            </table>
        </body>
    </html>
</xsl:template>

<!-- tabulate series data -->
<xsl:template match="series" mode="movieEntity">
    <xsl:param name="depth"/>
    <tr >
        <td>
            <!-- pad the title to reflect the recursion depth -->
            <xsl:call-template name="pad">
                <xsl:with-param name="padChar" select="'|--'"/>
                <xsl:with-param name="padCount" select="$depth"/>
            </xsl:call-template>
            <b>
                <xsl:value-of select="title"/>
            </b>
        </td>
        <td/><td/><td/><td/>
    </tr>
    <xsl:apply-templates mode="movieEntity">
        <!-- add one to the recursion depth -->
        <xsl:with-param name="depth" select="$depth+1"/>
    </xsl:apply-templates>
</xsl:template>

<!-- tabulate movie data -->
<xsl:template match="movie" mode="movieEntity">
    <xsl:param name="depth"/>
    <tr >
	    <td >
            <!-- pad the title to reflect the recursion depth -->
            <xsl:call-template name="pad">
                <xsl:with-param name="padChar" select="'|--'"/>
                <xsl:with-param name="padCount" select="$depth"/>
            </xsl:call-template>
            <xsl:value-of select="title"/>
        </td>
	    <td ><xsl:value-of select="date"/></td>
        <td ><xsl:apply-templates select="director"/></td>
        <td ><xsl:apply-templates select="star"/></td>
        <td ><xsl:apply-templates select="genre"/></td>
    </tr>
</xsl:template>

<!-- format directors as comma-delimited list -->
<xsl:template match="director">
    <xsl:value-of select="."/>
    <xsl:if test="not(position()=last())">, </xsl:if>
</xsl:template>

<!-- format stars as comma-delimited list -->
<xsl:template match="star">
    <xsl:value-of select="."/>
    <xsl:if test="not(position()=last())">, </xsl:if>
</xsl:template>

<!-- format genres as comma-delimited list -->
<xsl:template match="genre">
    <xsl:value-of select="."/>
    <xsl:if test="not(position()=last())">, </xsl:if>
</xsl:template>


<!-- For non-whitespace characters, you can call pad directly: -->
<!--
  <h1>25 '@' Symbols:</h1>
  <xsl:call-template name="pad">
   <xsl:with-param name="padChar" select="'@'"/>
   <xsl:with-param name="padCount" select="25"/>
  </xsl:call-template>
-->
  <!-- For whitespace characters, things are a little more complicated. Use
a non-whitespace character to generate the content, then pass that into a
temporary variable. Then use the translate() function to map the
non-whitespace character to a white-space one: -->
<!--
  <xsl:variable name="pad.tmp"><xsl:call-template name="pad"><xsl:with-param
name="padCount" select="25"/></xsl:call-template></xsl:variable>
  <xsl:variable name="pad" select="translate($pad.tmp,'#',' ')"/>
  <h1>25 Empty Spaces:</h1>
  <pre>.<xsl:value-of select="$pad"/>.</pre><br/>
-->

<!-- generate a string of non-whitespace pad characters (can use multiple 
characters) 
-->
<xsl:template name="pad">
    <!-- the pad character -->
    <xsl:param name="padChar" select="'#'"/>
    <!-- the pad count -->
    <xsl:param name="padCount" select="0"/>
    <!-- print nothing if the count is zero -->
    <xsl:if test="$padCount&gt;0">
        <xsl:value-of select="$padChar"/>
    </xsl:if>
    <!-- recursively add padding to the value of the count -->
    <xsl:if test="$padCount&gt;1">
        <xsl:call-template name="pad">
            <xsl:with-param name="padCount" select="number($padCount) - 1"/>
            <xsl:with-param name="padChar" select="$padChar"/>
        </xsl:call-template>
    </xsl:if>
</xsl:template>


<!-- clear unwanted text -->
<xsl:template match="text()" mode="movieEntity"/>

<!-- clear attributes - not needed -->
<!--xsl:template match="@*">
    <xsl:attribute name="{name()}" />
</xsl:template-->

<!-- print out debug messages for unrecognised nodes - not needed -->
<!--xsl:template match="*">
    <xsl:message terminate="no">
        WARNING: Unmatched element: <xsl:value-of select="name()"/>
    </xsl:message>

    <xsl:apply-templates/>
</xsl:template-->

</xsl:stylesheet>
